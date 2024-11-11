import requests
from terminaltables import AsciiTable
from environs import Env


def predict_rub_salary_for_superjob(vacancy):

        if vacancy['currency'] != 'rub':
            return None
        else:
            if vacancy['payment_from'] and vacancy['payment_to']:
                return vacancy['payment_to']  - vacancy['payment_from']
            elif vacancy['payment_from']:
                return vacancy['payment_from']*1.2
            elif vacancy['payment_to']:
                return vacancy['payment_to']*0.8

def sj_vacancies_stats(prog_languages, sj_secret_key):

        languages_and_vacancies = {}
        sj_url = 'https://api.superjob.ru/2.0/vacancies'

        for language in prog_languages:
            page = 5
            count = 100

            all_salary = 0
            number_salary = 0

            languages_and_vacancies[language] = {}

            while page>0:

                headers = {
                    'X-Api-App-Id': sj_secret_key
                }

                params = {
                    'profession': 'программист' + language,
                    'town': 4,
                    'catalogues': 48,
                    'page': page,
                    'count': count,
                }

                response = requests.get(sj_url,headers=headers, params=params)
                response.raise_for_status()
                vacancies = response.json()
                all_vacancies_number = vacancies['total']

                for vacancy in vacancies['objects']:
                    
                    salary = predict_rub_salary_for_superjob(vacancy)

                    if salary:
                        number_salary+=1
                        all_salary+=int(salary)

                page-=1

            avg_salary = all_salary // number_salary
            
            languages_and_vacancies[language]['vacancies_found'] = all_vacancies_number
            languages_and_vacancies[language]['vacancies_processed'] = number_salary
            languages_and_vacancies[language]['average_salary'] = avg_salary

        return languages_and_vacancies

def predict_rub_salary_for_hh(vacancy):

    vacancy_salary = vacancy['salary']

    if not vacancy_salary or vacancy_salary['currency'] != 'RUR':
        return None
    else:
        if vacancy_salary['from'] and vacancy_salary['to']:
            return vacancy_salary['to'] - vacancy_salary['from']
        elif vacancy_salary['from']:
            return vacancy_salary['from']*1.2
        elif vacancy_salary['to']:
            return vacancy_salary['to']*0.8
 
def hh_vacancies_stats(prog_languages):

    languages_and_vacancies = {}
    hh_url = 'https://api.hh.ru/vacancies/'

    for language in prog_languages:
        page = 19
        per_page = 100

        all_salary = 0
        number_salary = 0

        languages_and_vacancies[language] = {}

        while page>0:

            params = {
            'text': 'программист' + language,
            'area': '1',
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
                    number_salary+=1
                    all_salary+=int(salary)

            page-=1

        avg_salary = all_salary // number_salary
        
        languages_and_vacancies[language]['vacancies_found'] = all_vacancies_number
        languages_and_vacancies[language]['vacancies_processed'] = number_salary
        languages_and_vacancies[language]['average_salary'] = avg_salary

    return languages_and_vacancies

def hh_vacanies_stats_table(prog_languages):
    
    vacansies_statistics = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

    for language, statistics in hh_vacancies_stats(prog_languages).items():
        row = [language, statistics['vacancies_found'], statistics['vacancies_processed'], statistics['average_salary']]
        vacansies_statistics.append(row)

    return AsciiTable(vacansies_statistics, 'HeadHunter Moscow').table

def sj_vacancies_stats_table(prog_languages):

    vacansies_statistics = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

    for language, statistics in sj_vacancies_stats(prog_languages).items():
        row = [language, statistics['vacancies_found'], statistics['vacancies_processed'], statistics['average_salary']]
        vacansies_statistics.append(row)

    return AsciiTable(vacansies_statistics, 'SuperJob Moscow').table

def main():

    prog_languages = ['Python', 'Java', 'Javascript']

    env = Env()
    env.read_env()

    sj_secret_key = env.str('SJ_SECRET_JEY')

    print(hh_vacanies_stats_table(prog_languages))
    print()
    print(sj_vacancies_stats_table(prog_languages, sj_secret_key))

if __name__ == '__main__':
    main()
    