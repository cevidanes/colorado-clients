from flask import Flask, request, jsonify, Blueprint, render_template
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import datetime
from utilities.extensions import db
from models.contracts.contracts import CPContractStage, CPContractsImport,CPContract
from models.clients.clients import CPClientStage, CPClient

contracts = Blueprint('contracts', __name__, template_folder='templates')

def read_excel_file(file):
    """
    Reads an Excel file and returns a pandas DataFrame.

    Args:
    file (FileStorage): The Excel file to read.

    Returns:
    DataFrame: A pandas DataFrame containing the data from the Excel file.
    Error: An error message if the file is invalid.
    """
    try:
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
            
            return unique_df, "Nexus"
    except Exception as e:
        return jsonify({"error": "Arquivo inválido!"}), 401

def create_import_control_row(file):
    """
    Creates an import control row for the given file.

    Args:
    file (str): The name of the file.

    Returns:
    CPContractsImport: The import control row.
    Error: An error message if the file has already been imported.
    """
    # Check if the file has already been imported
    import_control = CPContractsImport.query.filter_by(file_name=file.filename).first()
    if import_control:
        # Return an error message if the file has already been imported
        return {"error": "Arquivo já importado!"}, 402

    try:
        # Create a new import control row
        import_control = CPContractsImport(file_name=file.filename)

        # Add the import control row to the database
        db.session.add(import_control)
        db.session.commit()

        # Return the import control row
        return import_control

    except Exception as e:
        # Rollback the database transaction if an exception is raised
        db.session.rollback()

        # Return an error message if an exception is raised
        return {"error": "Error ao criar o registro de Controle para importação contate o Administrador" + str(e)}, 500

def create_clients_row(client_data, import_control, df_type):
    """
    Creates clients and contracts in Stage Table.

    Args:
    file (str): The name of the file.

    Returns:
    CPContractsImport: The import control row.
    Error: An error message if cpf is invalid.
    """
    total_clients_imported = 0
    total_clients_for_update = 0
    total_clients_for_insert = 0
   
    #try:
    unique_client_df = client_data.drop_duplicates(subset=['name', 'doc'])

    for index, row in unique_client_df.iterrows():
            # Check if a record exists with the same file_name, cpf_cnpj, and name for this client
            try:
                clear_cpf_cnpj = int(row['doc'].replace('.','').replace('-','').replace('/',''))
            except Exception as e:
                db.session.rollback()
                import_control.status = "Error"
                db.session.commit()
                return jsonify({"error": "CPF/CNPJ inválido! Contrato: " + row['contract']}), 500
                                
            current_client = db.session.query(CPClient).filter(CPClient.name == row['name'], CPClient.cpf_cnpj == clear_cpf_cnpj).first()
            
            # Create and add a new record for Clients Stage Table, If Client is already in the main table it will be add the current client id
            if current_client:
                total_clients_for_update=total_clients_for_update+1
                client_stage = CPClientStage(
                    name=row['name'],
                    cpf_cnpj=clear_cpf_cnpj,
                    client_id = current_client.id,
                    import_id = import_control.id
                )
            else:
                total_clients_for_insert=total_clients_for_insert+1
                client_stage = CPClientStage(
                    name=row['name'],
                    cpf_cnpj=clear_cpf_cnpj,
                    import_id = import_control.id
                )
            
            db.session.add(client_stage)
            total_clients_imported= total_clients_imported+1
    import_control.total_clients_imported = total_clients_imported
    import_control.total_clients_for_update = total_clients_for_update
    import_control.total_clients_for_insert = total_clients_for_insert
    db.session.commit()
    
    return True
    #except Exception as e:
     #   db.session.rollback()
    #    return jsonify({"Error": "Erro ao inserir os Clientes. Contate o Administrador." + str(e)}), 400
     

def create_contracts_row(contract_data, import_control, df_type):
    """
    Creates contracts in Stage Table.

    Args:
    contract_data (DataFrame): The contract data.
    import_control (CPContractsImport): The import control row.
    df_type (str): The type of the DataFrame.

    Returns:
    Response: A response indicating whether the contracts were added successfully or not.
    """
    total_contracts_imported = 0
    total_contracts_for_update = 0
    total_contracts_for_insert = 0
    if df_type =="Nexus":
        try:
            unique_contract_df = contract_data.drop_duplicates(subset=['contract', 'name', 'doc','unidades'])
            for index, row in unique_contract_df.iterrows():
                # Check if a record exists with the same file_name, cpf_cnpj, and name for this client
                try:
                    clear_cpf_cnpj = int(row['doc'].replace('.','').replace('-','').replace('/',''))
                except Exception as e:
                    db.session.rollback()
                    import_control.status = "Error"
                    db.session.commit()
                    return jsonify({"error": "CPF/CNPJ inválido! Contrato: " + row['contract']}), 500
                
                contract_code = "N" + str(int(row['contract']))
                # Check if a record exists with the same file_name, contract, and name for this contract
                current_contract = db.session.query(CPContract).filter(CPContract.contract_code == contract_code, CPContract.cpf_cnpj == clear_cpf_cnpj).first()

                # Create and add a new record for Contracts Stage Table, If Contract is already in the main table it will be add the current contract id
                if current_contract:
                    total_contracts_for_update = total_contracts_for_update + 1
                    contract_stage = CPContractStage(
                        contract_code=contract_code,
                        doc=clear_cpf_cnpj,
                        contract_id=current_contract.id,
                        import_id=import_control.id,
                        lote=row['unidades']
                        
                    )
                else:
                    total_contracts_for_insert = total_contracts_for_insert + 1
                    contract_stage = CPContractStage(
                        contract_code=contract_code,
                        doc=clear_cpf_cnpj,
                        import_id=import_control.id,
                        lote=row['unidades']
                    )

                db.session.add(contract_stage)
                total_contracts_imported = total_contracts_imported + 1
            
            import_control.total_contracts_imported = total_contracts_imported
            import_control.total_contracts_for_update = total_contracts_for_update
            import_control.total_contracts_for_insert = total_contracts_for_insert
            db.session.commit()

            return True
        except Exception as e:
            db.session.rollback()
            return jsonify({"Error": "Erro ao inserir os Contratos. Contate o Administrador." + str(e)}), 400
    else:
        db.session.rollback()
        return jsonify({"Error": "Planilha não suportada. Contate o Administrador."}), 400
        
@contracts.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "Envie ao menos um arquivo."}), 400
        
    file = request.files['file']
    try:
        # Read the Excel file
        dfContracts, df_type = read_excel_file(file)
        
        #check if excel is loaded
        if isinstance(dfContracts, tuple):
            return dfContracts
    
        #Create import control row for the sended file
        import_control = create_import_control_row(file)
        
        #check if excel is loaded
        if isinstance(import_control, tuple):
            return import_control
   
        #import clients
        create_clients = create_clients_row(dfContracts, import_control, df_type)
        #check if excel is loaded
        if isinstance(create_clients, tuple):
            return create_clients
        
        #import contracts
        create_contracts = create_contracts_row(dfContracts, import_control, df_type)
        
        #check if excel is loaded
        if isinstance(create_contracts, tuple):
            return create_contracts

        import_control.status="Pronto para Importar"
        db.session.commit()
        return jsonify({"success": True, "message": "Imported to Stage finish"}), 201

    except Exception as e:
        db.session.rollback()
        #import_control.status = "Error"
        #db.session.commit()
        return jsonify({"error": str(e)}), 500

@contracts.route('/home')
def home():
    return render_template('contracts/home.html')
