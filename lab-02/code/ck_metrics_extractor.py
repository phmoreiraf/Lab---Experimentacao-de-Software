import pandas as pd

import os
import subprocess
import sys
import shutil
import time

import zipfile

def clone_zip_repo(repo_url, dest_dir):
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.makedirs(dest_dir, exist_ok=True)

    zip_path = os.path.join(dest_dir, "repo.zip")
    result = os.system(f"curl -L {repo_url} -o {zip_path}")
    if result != 0:
        raise Exception(f"Erro ao baixar o repositório {repo_url}")

   
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)
        root_folder = zip_ref.namelist()[0].split("/")[0]
    

    return os.path.join(dest_dir, root_folder)



def delete_repo(repo_dir):
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)

def run_ck(df):

    for index, row in df.iterrows():
        repo_name = row['nameWithOwner']
        default_branch = row['defaultBranchRef']
        print(f"Processando repositório {repo_name} (branch: {default_branch})...")

        base_dir = os.path.join("..\\data", "metrics_raw", repo_name.replace("/", "_"))
        os.makedirs(base_dir, exist_ok=True)

        output_dir = os.path.join(base_dir, "ck_output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Clona o repositório
        zip_url = f"https://github.com/{repo_name}/archive/refs/heads/{default_branch}.zip"
        print(f"[+] Clonando {zip_url} ...")
        repo_dir = os.path.join(base_dir, "source")
        try:
            repo_dir = clone_zip_repo(zip_url, repo_dir)

        except Exception as e:
            print(f"Erro: {e}")
            continue

        """
        Executa o CK Tool e retorna os caminhos para os arquivos .csv gerados.
        """
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

        print(f"[+] Executando CK Tool nas fontes em {repo_dir} ...")

        jar_path = os.path.join("ck", "target", "ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar")
        
        cmd = [
            'java', '-jar', jar_path,
            repo_dir,
            'true',      # usar JARs
            '0',         # max files per partition = automático
            'true',      # extrair métricas de variáveis e campos
            output_dir + os.sep
        ]

        time.sleep(1)

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print("Erro ao executar o CK:", e)
            sys.exit(1)

        # Caminhos para os arquivos gerados
        files = {
            'class': os.path.join(output_dir, 'class.csv'),
            'field': os.path.join(output_dir, 'field.csv'),
            'method': os.path.join(output_dir, 'method.csv'),
            'variable': os.path.join(output_dir, 'variable.csv'),
        }

        # Confirma se class.csv existe
        if not os.path.exists(files['class']):
            print("Erro: class.csv não encontrado.")
            sys.exit(1)

        # Confirma se field.csv existe (aviso)
        if not os.path.exists(files['field']):
            print("Aviso: field.csv não encontrado. Métricas de campos não estarão disponíveis.")

        # Confirma se method.csv existe (aviso)
        if not os.path.exists(files['method']):
            print("Aviso: method.csv não encontrado. Métricas por método não estarão disponíveis.")

        # Confirma se variable.csv existe (aviso)
        if not os.path.exists(files['variable']):
            print("Aviso: variable.csv não encontrado. Métricas de variáveis não estarão disponíveis.")

        print(f"[OK] Métricas salvas em {output_dir}")
        

