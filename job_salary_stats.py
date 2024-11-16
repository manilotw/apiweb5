import requests
from terminaltables import AsciiTable
from environs import Env


def calculate_rub_salary(payment_from, payment_to, currency):
    if currency not in ['RUR', 'rub']:
        return None
    
    if payment_from and payment_to:
        return payment_to - payment_from
    elif payment_from:
        return payment_from * 1.2
    elif payment_to:
        return payment_to * 0.8
    
    return None

def predict_rub_salary_for_sj(vacancy):
        
    payment_from = vacancy['payment_from']
    payment_to = vacancy['payment_to']
    currency = vacancy['currency'] 

    return calculate_rub_salary(payment_from, payment_to, currency)

def get_sj_vacancies_stats(prog_languages, sj_secret_key):
    sj_url = 'https://api.superjob.ru/2.0/vacancies/'
    languages_and_vacancies = {}

    for language in prog_languages:
        page = 0  
        per_page = 100
        all_salary = 0
        number_salary = 0

        languages_and_vacancies[language] = {}

        while True:

            headers = {
                    'X-Api-App-Id': sj_secret_key
                }
            
            params = {
                'keywords': 'программист ' + language,
                'town': 'Москва',
                'page': page,
                'count': per_page
            }

            response = requests.get(sj_url,headers=headers, params=params)
            response.raise_for_status()
            vacancies = response.json()

            all_vacancies_number = vacancies['total']
            for vacancy in vacancies['objects']:
                salary = predict_rub_salary_for_sj(vacancy)
                if salary:
                    number_salary += 1
                    all_salary += int(salary)

        
            if not vacancies.get('more', False):
                break

            page += 1  

        avg_salary = all_salary // number_salary if number_salary else 0

        languages_and_vacancies[language] = {
            'vacancies_found': all_vacancies_number,
            'vacancies_processed': number_salary,
            'average_salary': avg_salary
        }

    return languages_and_vacancies

def predict_rub_salary_for_hh(vacancy):

    vacancy_salary = vacancy['salary']

    if vacancy_salary:
        salary_from = vacancy_salary['from']
        salary_to = vacancy_salary['to']
        currency = vacancy_salary['currency']
    else:
        return None

    return calculate_rub_salary(salary_from, salary_to, currency)
 
def get_hh_vacancies_stats(prog_languages):

    hh_url = 'https://api.hh.ru/vacancies/'
    languages_and_vacancies = {}

    for language in prog_languages:
        page = 0 
        per_page = 100
        all_salary = 0
        number_salary = 0

        languages_and_vacancies[language] = {}
        area = 1
        while True:
            params = {
                'text': 'программист ' + language,
                'area': area,  
                'page': page,
                'per_page': per_page
            }

            response = requests.get(hh_url, params=params)
            response.raise_for_status()
            vacancies = response.json()

            all_vacancies_number = vacancies['found']
            for vacancy in vacancies['items']:
                salary = predict_rub_salary_for_hh(vacancy)
                if salary:
                    number_salary += 1
                    all_salary += int(salary)

            if 'pages' in vacancies and page >= vacancies['pages'] - 1:
                break

            page += 1  

        avg_salary = all_salary // number_salary if number_salary else 0

        languages_and_vacancies[language] = {
            'vacancies_found': all_vacancies_number,
            'vacancies_processed': number_salary,
            'average_salary': avg_salary
        }

    return languages_and_vacancies

def build_hh_vacancies_stats(prog_languages):

    vacansies_statistics = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

    for language, statistics in get_hh_vacancies_stats(prog_languages).items():
        row = [language, statistics['vacancies_found'], statistics['vacancies_processed'], statistics['average_salary']]
        vacansies_statistics.append(row)

    return vacansies_statistics

def get_hh_vacancies_stats_table(prog_languages):
    vacansies_statistics = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

    for language, statistics in get_hh_vacancies_stats(prog_languages).items():
        row = [language, statistics['vacancies_found'], statistics['vacancies_processed'], statistics['average_salary']]
        vacansies_statistics.append(row)

    return AsciiTable(vacansies_statistics, 'HeadHunter Moscow').table

def build_sj_vacancies_stats(prog_languages):

    vacansies_statistics = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

    for language, statistics in get_sj_vacancies_stats(prog_languages).items():
        row = [language, statistics['vacancies_found'], statistics['vacancies_processed'], statistics['average_salary']]
        vacansies_statistics.append(row)

    return vacansies_statistics

def get_sj_vacancies_stats_table(prog_languages, sj_secret_key):
    vacansies_statistics = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

    for language, statistics in get_sj_vacancies_stats(prog_languages, sj_secret_key).items():
        row = [language, statistics['vacancies_found'], statistics['vacancies_processed'], statistics['average_salary']]
        vacansies_statistics.append(row)

    return AsciiTable(vacansies_statistics, 'SuperJob Moscow').table

def main():

    prog_languages = ['Python', 'Java', 'Javascript']

    env = Env()
    env.read_env()

    sj_secret_key = env.str('SJ_SECRET_JEY')

    print(get_hh_vacancies_stats_table(prog_languages))
    print()
    print(get_sj_vacancies_stats_table(prog_languages, sj_secret_key))

if __name__ == '__main__':
    main()
    