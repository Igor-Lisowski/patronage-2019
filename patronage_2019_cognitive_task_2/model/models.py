from django.db import models
import pandas as pd
import math

class Person(models.Model):
	worked_years = models.FloatField(default = None)
	salary_brutto = models.FloatField(default = None, blank=True, null=True)

	@classmethod
	def create(cls, worked_years, salary_brutto):
		person = cls(worked_years=worked_years, salary_brutto=salary_brutto)
		return person

	@staticmethod
	def read_persons(file_name):
		return pd.read_csv(file_name, sep=',')
