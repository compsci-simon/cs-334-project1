from flask import Flask, render_template, url_for, redirect, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from scraper import scrape_github, github_api
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = '13274725f0a056d8'

class SearchForm(FlaskForm):
	search_terms = StringField("Search Form", validators=[DataRequired()])
	submit1 = SubmitField("Scrape Github")
	submit2 = SubmitField("Github API")

@app.route("/", methods=['GET', 'POST'])
def home():
	form = SearchForm()
	if form.validate_on_submit():
		items = []
		if form.submit1.data:
			string_items = scrape_github(form.search_terms.data).replace("None", "null").replace("'", '"')
			string_items = string_items.replace('repo_name', '"repo_name"').replace('description', '"description"')
			string_items = string_items.replace('tags', '"tags"').replace('num_stars', '"num_stars"').replace('language', '"language"')
			string_items = string_items.replace('license:', '"license":').replace('last_update', '"last_update"').replace('num_issues', '"num_issues"')
			items = json.loads(string_items)
			session['search_type'] = "scrape" 
		else:
			string_items = github_api(form.search_terms.data).replace("None", "null")
			string_items = string_items.replace('repo_name', '"repo_name"').replace('description', '"description"')
			string_items = string_items.replace('tags', '"tags"').replace('num_stars', '"num_stars"').replace('language', '"language"')
			string_items = string_items.replace('license:', '"license":').replace('last_update', '"last_update"').replace('num_issues', '"num_issues"')
			string_items = string_items.replace('has_issues:', '"has_issues":')
			items = json.loads(string_items)
			session['search_type'] = "API"
		session['list'] = items
		session['search_term'] = form.search_terms.data
		return redirect(url_for('display_results'))
	return render_template("index.html", form=form, legend="Search Github")

@app.route("/results/")
def display_results():
	page = request.args.get('page', 1, type=int)
	results_list = session['list']
	search_term = session['search_term']
	type_of_search = session['search_type']
	return render_template("results.html", header="Results from github "+type_of_search, search_term=search_term, results_list=results_list)

if __name__ == "__main__":
	app.run(debug=False)