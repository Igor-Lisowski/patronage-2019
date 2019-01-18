from django.http import HttpResponse
from model.models import Person
from sklearn import linear_model
from sklearn import preprocessing
import pandas
import math

known_salaries_range = 47
links = '<a href="/">Main menu</a> <a href="/results">Results</a> <a href="/charts">Charts</a> <a href="/range">Range</a>'

#chartjs
from random import randint
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
from rest_framework.views import APIView
from rest_framework.response import Response
import numpy as np

#range
from django import forms

def mainmenu(request):
	global links
	return HttpResponse(links)

def results(request):
	persons = None
	if Person.objects.all().exists() == False:
		persons = Person.read_persons('salary.csv')

		worked_years = persons[['workedYears']]
		salaries_brutto = persons[['salaryBrutto']].apply(pandas.to_numeric, errors='coerce')

		#regression
		global known_salaries_range
		regression = get_trained_regression_model(worked_years, salaries_brutto, known_salaries_range)

		#find solution
		predicted_salaries_brutto = get_predicted_salaries_brutto(regression, worked_years, known_salaries_range)

		#print results
		print_predicted_salaries_brutto(worked_years[known_salaries_range:], predicted_salaries_brutto)

		add_persons_to_database(persons, predicted_salaries_brutto)

	#prepare results in html format
	html_response = get_results_in_html_format()

	return HttpResponse(html_response)

def add_persons_to_database(persons, predicted_salaries_brutto):
	global known_salaries_range
	worked_years = persons[['workedYears']]
	salaries_brutto = persons[['salaryBrutto']]
	for index, person in persons.iterrows():
		new_person = None
		new_salary_brutto = None
		if index < known_salaries_range:
			new_person = Person.create(worked_years=person['workedYears'], salary_brutto=person['salaryBrutto'])
		else:
			new_person = Person.create(worked_years=person['workedYears'], salary_brutto=predicted_salaries_brutto[index - known_salaries_range])
		new_person.save()

def get_trained_regression_model(worked_years, salaries_brutto, known_salaries_range):
	regression = linear_model.LinearRegression()
	regression.fit(worked_years[:known_salaries_range], salaries_brutto[:known_salaries_range])
	return regression

def get_predicted_salaries_brutto(regression, worked_years, known_salaries_range):
	return regression.predict(worked_years[known_salaries_range:])
	
def print_predicted_salaries_brutto(worked_years, predicted_salaries_brutto):
	print('Results:')
	print('workedYears' + ' ' + 'salaryBrutto')
	for i in range(predicted_salaries_brutto.size):
		print(str(worked_years.get_values()[i, 0]) + '        '  + str(predicted_salaries_brutto[i, 0]))

def get_results_in_html_format():
	persons = Person.objects.all()
	global links
	html_format = "<!DOCTYPE html>" + "<html>" + "<head>" + links + "<style>" + "table, th, td {" +	"border: 1px solid black;" + "}" + "</style>" + "</head>" + "<body>" + "<table>" + "<tr>" + "<th>WorkedYears</th>" + "<th>salaryBrutto</th>" + "</tr>"
	for person in persons:
		html_format = html_format +  "<tr>" + "<td>" + str(person.worked_years) + "</td>" + "<td>" + str(person.salary_brutto) + "</td>" + "</tr>"
	html_format = html_format + "</table>" + "</body>" + "</html>"
	return html_format


class ChartView(View):
	def get(self, request, *args, **kwargs):
		global links
		args = {'links': links}
		return render(request, 'charts.html', args)


class ChartData(APIView):
	authentication_classes = []
	permission_classes = []

	def get(self, request, format=None):	
		global known_salaries_range

		worked_years = Person.objects.all().values_list('worked_years', flat=True)
		salaries_brutto = Person.objects.all().values_list('salary_brutto', flat=True)

		labels = []
		
		default_items = []

		colors = ChartData.get_colors_for_salaries(salaries_brutto)

		data = {
		"labels": worked_years,
		"default": salaries_brutto,
		"colors": colors,
		}
		return Response(data)

	@staticmethod
	def get_colors_for_salaries(salaries_brutto):
		colors = []
		for sb in np.nditer(salaries_brutto):
			if sb < 4000:
				colors.append('rgba(191, 255, 0, 1)')
			elif 4000 <= sb and sb < 6000:
				colors.append('rgba(255, 255, 0, 1)')
			elif 6000 <= sb and sb < 8000:
				colors.append('rgba(255, 191, 0, 1)')
			elif 8000 <= sb and sb <= 10000:
				colors.append('rgba(255, 128, 0, 1)')
			else:
				colors.append('rgba(255, 64, 0, 1)')
		return colors


class RangeView(TemplateView):
	template_name='range.html'

	def get(self, request):
		form = RangeForm()
		global links
		return render(request, self.template_name, {'form': form, 'links': links})

	def post(self, request):
		form = RangeForm(request.POST)
		html_response = "<!DOCTYPE html>" + "<html>"
		if form.is_valid():
			post_response = form.cleaned_data['post']

			if RangeView.check_if_input_is_valid(post_response) == True:

				range_numbers = [int(number) for number in post_response.split(':')]

				html_response = html_response + "<head>" + links + "<style>" + "table, th, td {" +	"border: 1px solid black;" + "}" + "</style>" + "</head>" + "<body>" + "<table>" + "<tr>" + "<th>WorkedYears</th>" + "<th>salaryBrutto</th>" + "</tr>"
				persons = Person.objects.all()
				for person in persons:
					if range_numbers[0] <= person.worked_years and person.worked_years <= range_numbers[1]:
						html_response = html_response +  "<tr>" + "<td>" + str(person.worked_years) + "</td>" + "<td>" + str(person.salary_brutto) + "</td>" + "</tr>"
				html_response = html_response + "</table>" + "</body>" + "</html>"
			else:
				html_response = html_response + "<h1>Error</h1>" + "<h2>Wrong input</h2>" + "</html>"
		return HttpResponse(html_response)

	@staticmethod
	def check_if_input_is_valid(post_response):
		string_range_numbers = [string_number for string_number in post_response.split(':')]

		for srn in string_range_numbers:
			try:
				int(srn)
			except ValueError:
				return False

		range_numbers = [int(number) for number in post_response.split(':')]

		if len(range_numbers) != 2:
			return False
		if range_numbers[0] < 0 or range_numbers[1] < 0:
			return False
		if range_numbers[0] > range_numbers[1]:
			return False
		return True


class RangeForm(forms.Form):
	post = forms.CharField()