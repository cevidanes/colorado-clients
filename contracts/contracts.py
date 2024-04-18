from flask import Flask, request, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import datetime
from utilities.extensions import db
from models.contracts.contracts import CPContractStage
from models.clients.clients import CPClientStage, CPClient

contracts = Blueprint('contracts', __name__, template_folder='templates')


@contracts.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "Envie ao menos um arquivo."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Envie ao menos um arquivo. - 02"}), 401
    
    if file.filename == '':
        return jsonify({"error": "Envie ao menos um arquivo."}), 402

    v_file_name = file.filename  # This is the file name of the uploaded file
    
    try:
        # Read the Excel file
        df = pd.read_excel(file, engine='openpyxl')
        df.columns = ['contract', 'name', 'C', 'D', 'doc', 'F', 'G', 'H', 'email', 'J', 'K', 'L']
        df['contract'] = pd.to_numeric(df['contract'], errors='coerce')
        new_df = df[df['contract'].notna()]
        new_df = new_df.drop_duplicates()
        new_df['unidades'] = None
        
        for value in new_df['doc'].unique():
            last_index = new_df[new_df['doc'] == value].index[-1]
            if last_index + 1 in df.index:
                new_df.loc[new_df['doc'] == value, 'unidades'] = df.loc[last_index + 1, 'doc']
        
        unique_df = new_df.drop_duplicates(subset=['contract','name', 'doc', 'unidades'])
        
        # Insert data into the database
        total_clients_imported =0
        for index, row in unique_df.iterrows():
            # Check if a record exists with the same file_name, cpf_cnpj, and name for this client
            clear_cpf_cnpj = int(row['doc'].replace('.','').replace('-','').replace('/',''))
            
            #same file same client delete
            existing_client_stage = CPClientStage.query.filter_by(name=row['name'], cpf_cnpj=clear_cpf_cnpj).first()
            if existing_client_stage.load_file_name != v_file_name:
                return jsonify({"error": "Existem clientes na sua planilha com processo de importação pendente!", "Details": "NOME: " +  row['name'] + " CPF/CNPJ: " + row['doc'] + " ARQUIVO: " + existing_client_stage.load_file_name }), 500
            else:
                # If a matching record is found, delete it
                db.session.delete(existing_client_stage)
                db.session.commit()
               
            current_client = CPClient.query.filter_by(name=row['name'], cpf_cnpj=clear_cpf_cnpj).first()
            
            # Create and add a new record for Clients Stage Table, If Client is already in the main table it will be add the current client id
            if current_client:
                client_stage = CPClientStage(
                    name=row['name'],
                    cpf_cnpj=clear_cpf_cnpj,
                    load_file_name=v_file_name,
                    client_id = CPClient.id
                )
            else:
                client_stage = CPClientStage(
                    name=row['name'],
                    cpf_cnpj=clear_cpf_cnpj,
                    load_file_name=v_file_name
                )
            
            db.session.add(client_stage)
            total_clients_imported= total_clients_imported+1
            
        db.session.commit()

        return jsonify({"message": "File processed and data added successfully" + str(total_clients_imported)}), 200
    
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
