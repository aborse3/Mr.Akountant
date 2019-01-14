# Mr. Akountant
## Who is Mr. Akountant?
- Mr. Akountant is a google assistant application which I build at BigRed Hack 2018. It helps user to keep track of the expenses.
- Users can talk to Mr. Akountant using voice commands and he will save the expenses in the particular category. Later, user can ask Mr. Akountant how much did they spend on a particular category in any given time.
- Google DialogFlow converts voice commands into http request which invokes AWS lambda function in the backend. Expenses are stored in Postgresql.
- All the pyhton dependencies are listed in requirements.txt

## How does it work?
- [Demo video](https://www.youtube.com/watch?v=y9J4cQ_F8Og)

## How to set up?
- Import akountant.zip to your Google DialogFlow account. This will create all the NLP frontend for this project.
- Create AWS lambda
- Create Postgresql instance and change the credentials in database.ini
- Clone the repository
```bash
pip install requirements.txt
```
- push the deplpoyment package to AWS lambda
- Do not forget to give AWS lambda's endpoint to DialogFlow
