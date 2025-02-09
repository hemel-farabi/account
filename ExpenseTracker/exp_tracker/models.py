from django.db import models
from datetime import datetime



class Account(models.Model):
    name = models.CharField(max_length=100)
    expense = models.FloatField(default=0)
    user = models.ForeignKey('auth.user', on_delete=models.CASCADE)
    expense_list = models.ManyToManyField('Expense', blank=True)

class Expense(models.Model):
    name = models.CharField(max_length=100)
    amount = models.FloatField(default=0)
    date = models.DateField(null=False, default=lambda: datetime.now().date())
    long_term = models.BooleanField(default=False)
    interest_rate = models.FloatField(null=True, blank=True, default=0)  # Annual interest rate in percent
    end_date = models.DateField(null=True, blank=True)
    monthly_expense = models.FloatField(default=0, null=True, blank=True)
    user = models.ForeignKey('auth.user', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.long_term:
            self.monthly_expense = self.calculate_monthly_expense()
        super(Expense, self).save(*args, **kwargs)

    def calculate_monthly_expense(self):
        if self.long_term:
            # Ensure required dates are provided
            if not self.end_date or not self.date:
                return 0

            # Calculate approximate number of months between start and end dates
            days = (self.end_date - self.date).days
            months = days / 30  # approximate month count

            # If no interest, simply divide the amount by the number of months
            if self.interest_rate == 0:
                return self.amount / months if months > 0 else 0
            else:
                # Calculate monthly interest rate (convert annual percentage to a decimal)
                monthly_rate = self.interest_rate / 12 / 100

                # Calculate number of months from the current date until end_date
                current_date = datetime.now().date()
                total_months = (self.end_date.year - current_date.year) * 12 + (self.end_date.month - current_date.month)
                if total_months <= 0:
                    return self.amount

                # Use the amortization formula to calculate the monthly expense:
                # Payment = (P * r) / (1 - (1 + r) ** (-n))
                monthly_payment = (self.amount * monthly_rate) / (1 - (1 + monthly_rate) ** (-total_months))
                return monthly_payment
        else:
            # If not a long-term expense, return the current monthly_expense value
            return self.monthly_expense
