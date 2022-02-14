import requests
import print_functions as prt
import jobs_functions as jbs
import runs_functions as runsf
from unidecode import unidecode

def test_workflow(i, n, workflows, request_path, username, token, full_repo_path):
    n_runs, runs = runsf.runs_path(i, n, workflows, request_path, username, token) # Runs é o arquivo json com os dados das runs e n_runs o número de runs no workflow
    keywords_dict = {"clone":0, "compile":0, "build":0, "ci": 0, "maven":0, "tests":0, "test":0, "regression": 0} # Dicionário de palavras chaves relacionadas a automação de CI/CD
    if (n_runs < n): # Ignora o caso de Pipelines que não são utilizados, mas estão no actions do repo   
        for i in range(0, n_runs): # Faz o loop das funções para o máximo de runs dísponível, mesmo que menor que n
            keywords_dict = job_keywords_test(i, runs, keywords_dict, full_repo_path, username, token)                   
    else:   
        for i in range(0, n):
            keywords_dict = job_keywords_test(i, runs, keywords_dict, full_repo_path, username, token)
            
    return(keywords_dict)

def chr_remove(old, to_remove): # Função que remove caracteres especiais
    new_string = old.lower()
    for x in to_remove:
        new_string = new_string.replace(x, '')
    return new_string

def test_name(name, keywords_dict): # Função que testa existência da palavra dentro do dicionário
    name = chr_remove(name, "!@#$%¨&*()_-=+'?:<>,.\|^~`}{][;") # Remove caracteres especiais
    name = unidecode(name) # Remove acentos
    lista_palavras = name.split() # lista com as palavras da frase
    for palavra in lista_palavras: # testa de palavra em palavra com o dicionário
        if (palavra in keywords_dict):
            keywords_dict[palavra] += 1 # Caso encontre soma 1 ocorrência
    return(keywords_dict) # Retorna o dicionário

def test_job_name(j, jobs, keywords_dict): # Função que testa se o nome do Job da evidências de ser para CI/CD
    job_name = jobs[j].get("name") # Recupera o nome do Job
    keywords_dict = test_name(job_name, keywords_dict) # Testa o nome
    return(keywords_dict) # Retorna o dicionário

def test_steps_name(j, jobs, keywords_dict): # Função que testa se os passos do Job fornecem evidências de CI/CD
    steps = jobs[j].get("steps") # Entra na lista de steps
    n_steps = len(steps) # recupera quantidade de steps
    for k in range(n_steps):
        step_name = steps[k].get("name") # Recupera o nome do Job
        keywords_dict = test_name(step_name, keywords_dict) # Testa o nome
    return(keywords_dict) # Retorna o dicionário

def job_keywords_test(i, runs, keywords_dict, full_repo_path, username, token): # i percore o número de runs
    id_jobs = runs[i].get("id") # recupera id da run
    condition = runs[i].get("conclusion") 
    if (condition != "action_required"): # Verifica se a run não tem acesso privado
        path_jobs = full_repo_path + "/actions/runs/{0}/jobs".format(id_jobs) # define caminho para os jobs da run
        res_jobs = requests.get(path_jobs, auth= (username, token)) # Executa chamada para informações dos jobs
        jobs_json = res_jobs.json() # Transformar informações para formato json
        n_jobs = int(jobs_json["total_count"]) # Recupera a quantidade total de jobs
        jobs = jobs_json["jobs"] # Entra nas informações sobre os jobs
        for j in range(n_jobs): # Percore cada Job existente
            keywords_dict = test_job_name(j, jobs, keywords_dict) # Testa o nome do job
            keywords_dict = test_steps_name(j, jobs, keywords_dict) # Testa os passos do job
    return(keywords_dict)

