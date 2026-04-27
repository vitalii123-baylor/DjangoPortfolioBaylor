import json
import datetime
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from .models import Budget, BudgetCategory, Expense
from .views import resolve_icon, get_demo_user, get_dashboard_data


def make_user(username='testuser'):
    return User.objects.create_user(username=username, password='pass')


def make_budget(user, limit=1000):
    month_start = datetime.date.today().replace(day=1)
    budget = Budget.objects.create(
        user=user,
        current_month=month_start,
        total_monthly_limit=Decimal(str(limit)),
    )
    BudgetCategory.objects.create(budget=budget, name='Food & Drinks', icon='☕', limit=Decimal('500'))
    BudgetCategory.objects.create(budget=budget, name='Transport', icon='🚗', limit=Decimal('300'))
    return budget


def make_expense(user, amount, category='Food & Drinks', days_ago=0):
    date = timezone.now() - datetime.timedelta(days=days_ago)
    return Expense.objects.create(
        user=user,
        original_text=f'Expense {amount}',
        category=category,
        amount=Decimal(str(amount)),
        date=date,
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class BudgetModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.budget = make_budget(self.user, limit=1000)

    def test_str(self):
        expected = f"testuser — {datetime.date.today().strftime('%B %Y')}"
        self.assertEqual(str(self.budget), expected)

    def test_get_total_spent_no_expenses(self):
        self.assertEqual(self.budget.get_total_spent(), 0)

    def test_get_total_spent_with_expenses(self):
        make_expense(self.user, 200)
        make_expense(self.user, 150)
        self.assertEqual(float(self.budget.get_total_spent()), 350.0)

    def test_get_remaining(self):
        make_expense(self.user, 400)
        self.assertEqual(float(self.budget.get_remaining()), 600.0)

    def test_get_percentage(self):
        make_expense(self.user, 500)
        self.assertEqual(self.budget.get_percentage(), 50.0)

    def test_get_percentage_zero_limit(self):
        self.budget.total_monthly_limit = 0
        self.budget.save()
        self.assertEqual(self.budget.get_percentage(), 0)

    def test_get_percentage_over_budget(self):
        make_expense(self.user, 1200)
        self.assertEqual(self.budget.get_percentage(), 120.0)


class BudgetCategoryModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.budget = make_budget(self.user, limit=1000)
        self.food_cat = self.budget.categories.get(name='Food & Drinks')

    def test_str(self):
        self.assertIn('Food & Drinks', str(self.food_cat))

    def test_get_spent_no_expenses(self):
        self.assertEqual(self.food_cat.get_spent(), 0)

    def test_get_spent_matching_category(self):
        make_expense(self.user, 120, category='Food & Drinks')
        make_expense(self.user, 80, category='Food & Drinks')
        self.assertEqual(float(self.food_cat.get_spent()), 200.0)

    def test_get_spent_ignores_other_categories(self):
        make_expense(self.user, 100, category='Transport')
        self.assertEqual(self.food_cat.get_spent(), 0)

    def test_get_percentage(self):
        make_expense(self.user, 250, category='Food & Drinks')
        self.assertEqual(self.food_cat.get_percentage(), 50.0)

    def test_get_percentage_zero_limit(self):
        self.food_cat.limit = 0
        self.food_cat.save()
        self.assertEqual(self.food_cat.get_percentage(), 0)


class ExpenseModelTest(TestCase):

    def setUp(self):
        self.user = make_user()

    def test_str(self):
        exp = make_expense(self.user, 50, category='Transport')
        self.assertIn('Transport', str(exp))
        self.assertIn('50', str(exp))

    def test_default_ordering_newest_first(self):
        make_expense(self.user, 10, days_ago=2)
        make_expense(self.user, 20, days_ago=0)
        expenses = list(Expense.objects.filter(user=self.user))
        self.assertGreater(expenses[0].amount, expenses[1].amount)


# ---------------------------------------------------------------------------
# resolve_icon tests
# ---------------------------------------------------------------------------

class ResolveIconTest(TestCase):

    def test_known_keyword_returns_emoji(self):
        self.assertEqual(resolve_icon('coffee'), '☕')
        self.assertEqual(resolve_icon('car'), '🚗')

    def test_short_emoji_passthrough(self):
        self.assertEqual(resolve_icon('☕'), '☕')

    def test_unknown_long_string_returns_default(self):
        self.assertEqual(resolve_icon('unknown-icon-name'), '💰')


# ---------------------------------------------------------------------------
# get_demo_user tests
# ---------------------------------------------------------------------------

class GetDemoUserTest(TestCase):

    def test_creates_user_if_not_exists(self):
        self.assertFalse(User.objects.filter(username='demo').exists())
        user = get_demo_user()
        self.assertEqual(user.username, 'demo')

    def test_returns_existing_user_without_duplicate(self):
        get_demo_user()
        get_demo_user()
        self.assertEqual(User.objects.filter(username='demo').count(), 1)


# ---------------------------------------------------------------------------
# get_dashboard_data tests
# ---------------------------------------------------------------------------

class GetDashboardDataTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.budget = make_budget(self.user, limit=1000)

    def test_returns_required_keys(self):
        data = get_dashboard_data(self.user)
        for key in ('total_spent', 'total_limit', 'total_percentage', 'total_remaining',
                    'categories', 'daily_labels', 'daily_values', 'expenses'):
            self.assertIn(key, data)

    def test_daily_labels_has_seven_entries(self):
        data = get_dashboard_data(self.user)
        self.assertEqual(len(data['daily_labels']), 7)

    def test_expenses_capped_at_ten(self):
        for i in range(15):
            make_expense(self.user, 10)
        data = get_dashboard_data(self.user)
        self.assertLessEqual(len(data['expenses']), 10)

    def test_creates_budget_for_new_user(self):
        new_user = make_user('newuser')
        self.assertFalse(Budget.objects.filter(user=new_user).exists())
        get_dashboard_data(new_user)
        self.assertTrue(Budget.objects.filter(user=new_user).exists())


# ---------------------------------------------------------------------------
# View tests
# ---------------------------------------------------------------------------

class DashboardViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_dashboard_returns_200(self):
        response = self.client.get(reverse('expense_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_uses_correct_template(self):
        response = self.client.get(reverse('expense_dashboard'))
        self.assertTemplateUsed(response, 'expense_tracker/dashboard.html')


class AddExpenseViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    @patch('apps.expense_tracker.views.categorize_expense')
    def test_add_expense_creates_record(self, mock_cat):
        mock_cat.return_value = {'category': 'Food & Drinks', 'amount': 25.0, 'is_necessary': True, 'advice': 'Good choice!'}
        response = self.client.post(
            reverse('add_expense'),
            data=json.dumps({'text': 'Lunch $25'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(Expense.objects.first().category, 'Food & Drinks')

    @patch('apps.expense_tracker.views.categorize_expense')
    def test_add_expense_returns_dashboard_json(self, mock_cat):
        mock_cat.return_value = {'category': 'Transport', 'amount': 40.0, 'is_necessary': True, 'advice': 'Ok!'}
        response = self.client.post(
            reverse('add_expense'),
            data=json.dumps({'text': 'Taxi $40'}),
            content_type='application/json',
        )
        data = response.json()
        self.assertIn('total_spent', data)
        self.assertIn('categories', data)

    def test_add_expense_requires_post(self):
        response = self.client.get(reverse('add_expense'))
        self.assertEqual(response.status_code, 405)


class SeedDataViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_seed_creates_expenses(self):
        self.assertEqual(Expense.objects.count(), 0)
        response = self.client.post(reverse('seed_expenses'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Expense.objects.count(), 7)

    def test_seed_returns_dashboard_json(self):
        response = self.client.post(reverse('seed_expenses'))
        data = response.json()
        self.assertIn('total_spent', data)


class ClearDataViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        user = get_demo_user()
        make_expense(user, 100)
        make_expense(user, 200)

    def test_clear_removes_all_expenses(self):
        self.assertEqual(Expense.objects.count(), 2)
        self.client.post(reverse('clear_expenses'))
        self.assertEqual(Expense.objects.count(), 0)

    def test_clear_returns_dashboard_json(self):
        response = self.client.post(reverse('clear_expenses'))
        data = response.json()
        self.assertEqual(data['total_spent'], 0.0)


class UpdateBudgetViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        user = get_demo_user()
        make_budget(user, limit=1000)

    def test_update_budget_changes_limit(self):
        self.client.post(
            reverse('update_budget'),
            data=json.dumps({'limit': 3000}),
            content_type='application/json',
        )
        budget = Budget.objects.get(user__username='demo')
        self.assertEqual(float(budget.total_monthly_limit), 3000.0)

    def test_update_budget_returns_dashboard_json(self):
        response = self.client.post(
            reverse('update_budget'),
            data=json.dumps({'limit': 2000}),
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(data['total_limit'], 2000.0)


class GetAdviceViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_advice_no_expenses_returns_message(self):
        get_demo_user()
        response = self.client.get(reverse('get_advice'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('advice', data)
        self.assertIn('No expenses', data['advice'])

    @patch('apps.expense_tracker.views.generate_daily_advice')
    def test_advice_with_expenses_calls_gemini(self, mock_advice):
        mock_advice.return_value = 'I noticed you spend a lot on food! 🍔'
        user = get_demo_user()
        make_budget(user, limit=1000)
        make_expense(user, 50)
        response = self.client.get(reverse('get_advice'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['advice'], 'I noticed you spend a lot on food! 🍔')
        mock_advice.assert_called_once()

    @patch('apps.expense_tracker.views.generate_daily_advice')
    def test_advice_summary_contains_real_data(self, mock_advice):
        mock_advice.return_value = 'Great job!'
        user = get_demo_user()
        make_budget(user, limit=500)
        make_expense(user, 100, category='Food & Drinks')
        self.client.get(reverse('get_advice'))
        call_args = mock_advice.call_args[0][0]
        self.assertIn('100.00', call_args)
        self.assertIn('500.00', call_args)


class DeleteExpenseViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = get_demo_user()
        make_budget(self.user, limit=1000)

    def test_delete_removes_expense(self):
        exp = make_expense(self.user, 75)
        self.assertEqual(Expense.objects.count(), 1)
        self.client.post(reverse('delete_expense', args=[exp.pk]))
        self.assertEqual(Expense.objects.count(), 0)

    def test_delete_returns_dashboard_json(self):
        exp = make_expense(self.user, 75)
        response = self.client.post(reverse('delete_expense', args=[exp.pk]))
        data = response.json()
        self.assertIn('total_spent', data)
        self.assertEqual(data['total_spent'], 0.0)

    def test_delete_nonexistent_returns_404(self):
        response = self.client.post(reverse('delete_expense', args=[9999]))
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# claude_service tests
# ---------------------------------------------------------------------------

class CategorizeExpenseTest(TestCase):

    @patch('apps.expense_tracker.claude_service._get_client')
    def test_parses_valid_json_response(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.text = '{"category": "Food & Drinks", "amount": 15.0, "is_necessary": true, "advice": "Good!"}'
        mock_get_client.return_value.models.generate_content.return_value = mock_response

        from .claude_service import categorize_expense
        result = categorize_expense('Coffee $15')

        self.assertEqual(result['category'], 'Food & Drinks')
        self.assertEqual(result['amount'], 15.0)

    @patch('apps.expense_tracker.claude_service._get_client')
    def test_strips_markdown_code_block(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.text = '```json\n{"category": "Transport", "amount": 30, "is_necessary": true, "advice": "Ok"}\n```'
        mock_get_client.return_value.models.generate_content.return_value = mock_response

        from .claude_service import categorize_expense
        result = categorize_expense('Uber $30')

        self.assertEqual(result['category'], 'Transport')

    @patch('apps.expense_tracker.claude_service._get_client')
    def test_returns_fallback_on_api_error(self, mock_get_client):
        mock_get_client.return_value.models.generate_content.side_effect = Exception('API error')

        from .claude_service import categorize_expense
        result = categorize_expense('Something')

        self.assertEqual(result['category'], 'Other')
        self.assertIsNone(result['amount'])


class GenerateDailyAdviceTest(TestCase):

    @patch('apps.expense_tracker.claude_service._get_client')
    def test_returns_advice_text(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.text = 'I noticed you spend a lot! 💡'
        mock_get_client.return_value.models.generate_content.return_value = mock_response

        from .claude_service import generate_daily_advice
        result = generate_daily_advice('Total spent: $500')

        self.assertEqual(result, 'I noticed you spend a lot! 💡')

    @patch('apps.expense_tracker.claude_service._get_client')
    def test_returns_fallback_on_error(self, mock_get_client):
        mock_get_client.return_value.models.generate_content.side_effect = Exception('timeout')

        from .claude_service import generate_daily_advice
        result = generate_daily_advice('summary')

        self.assertIn('temporarily unavailable', result)
