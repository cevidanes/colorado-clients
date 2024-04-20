from flask import Flask, request, jsonify, Blueprint, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from utilities.extensions import db
from models.contracts.contracts import CPContractStage, CPContractsImport,CPContract
from models.clients.clients import CPClientStage, CPClient
import traceback

contracts = Blueprint('contracts', __name__, template_folder='templates')

from openpyxl import load_workbook
from flask import jsonify

def read_excel_nexus(sheet):
    # Data starts at row 7
    contracts = []
    current_contract = None
        
    for row in sheet.iter_rows(min_row=7, values_only=True):
            contract_id = "N" + str(row[0])
            name = row[1]
            cpf = row[4]
            unidades = row[2]
            if name is not None and not isinstance(name,int): 
                if (len(contract_id) > 1 and contract_id !="NNone") and name != "NOME":  # New contract or additional clients under current contract
                    if current_contract is None or (current_contract['contrato'] != contract_id):
                        # Start a new contract record
                        contracts_cpf =[]
                        current_contract = {
                            'contrato': contract_id,
                            'clientes': [],
                            'unidades': ''
                        }
                        
                    # Create a unique identifier for each client
                    if cpf not in contracts_cpf:
                        current_contract['clientes'].append({'nome': name, 'cpf': cpf})
                        contracts_cpf.append(cpf)
                
                if "UNIDADES:" in name:  # End of a contract
                    if current_contract:  # There should always be a current contract
                        current_contract['unidades'] = unidades
                        contracts.append(current_contract)
                        current_contract = None  # Reset for safety, although should end processing        
    return contracts

def read_excel_mega(sheet):
    # Data starts at row 7
    contracts = []
    current_contract = None
    contracts_cpf =[]
    contract_id=None
    name=None
    for row in sheet.iter_rows(min_row=4, values_only=True):
        cpf = 0
        if isinstance(row[4],int) or 'Participante' in str(row[0]):
            if ("M" + str(row[4]) != contract_id) and str(row[4]) !='None':
                contracts.append(current_contract)
                current_contract = None
                contract_id = "M" + str(row[4])
                contracts_cpf =[]
                current_contract = {
                'contrato': contract_id,
                'clientes': []            
                }
            
            try:
                int(row[1].replace('0',''))
                name = row[2]
            except Exception as e:
                name = row[1]
            
        if 'CPF' in str(row[0]) or 'CNPJ' in str(row[0]):
            cpf = row[1]
            if cpf not in contracts_cpf:
                current_contract['clientes'].append({'nome': name, 'cpf': cpf})
                contracts_cpf.append(cpf)
        
        #Trick to debug for a line
        #if '35001' in contract_id: 
        #    print(row)
        #    print(contract_id,name,cpf, current_contract)
        #    input()
        #print(contracts)
        
    contracts.pop(0)
    return contracts

def read_excel_file(file):
    """
    Reads an Excel file and processes the data based on specific business rules.

    Args:
    file (str): Path to the Excel file to read.

    Returns:
    list of dicts: Extracted and processed data from the Excel file.
    Error: An error message if the file is invalid.
    """
    #try:
    workbook = load_workbook(filename=file)
    sheet = workbook.active
    # Header starts at row 6
    headers_nexus = [cell.value for cell in sheet[6]]
    header_mega = [cell.value for cell in sheet[1]]
    
    if 'CÓDIGO' in headers_nexus[0]:
        return read_excel_nexus(sheet)
    
    if 'Unidade' in header_mega:
        return read_excel_mega(sheet)
    
    #except Exception as e:
    #    return jsonify({"error": "Arquivo inválido!"}), 401
 
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

def insert_contract_data(list_contracts, import_control):
    """
    Creates clients and contracts in Stage Table.

    Args:
    list_contracts (list of dicts): The data of clients to process.
    import_control (CPContractsImport): The import control row.

    Returns:
    bool: True if processing was successful, False otherwise.
    Error: An error message if cpf is invalid.
    """

    total_clients_imported = 0
    try:
        for contract in list_contracts:
            contract_stage = CPContractStage(
                contract_code=contract['contrato'],
                unidades=contract.get('unidades'),
            )
            db.session.add(contract_stage)
            
            for client in contract['clientes']:                
                client_stage = CPClientStage(
                    name=client['nome'],
                    cpf_cnpj=client['cpf'],
                    import_id=import_control.id
                )

            db.session.add(client_stage) #ToDo: Check if it will increase the total sessions in the database.
            total_clients_imported += 1

        import_control.total_clients_imported = total_clients_imported
        db.session.commit()

        return True
    except Exception as e:
        print(e)
        db.session.rollback()
        error_message = "Erro ao inserir os Clientes. Contate o Administrador. " + str(e) + "\n" + traceback.format_exc()
        return jsonify({"Error": error_message}), 400

@contracts.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "Envie ao menos um arquivo."}), 400
        
    file = request.files['file']
    
    import_control = create_import_control_row(file)
        
    #check if import control is ok.
    if isinstance(import_control, tuple):
        return import_control
    
    list_contracts = read_excel_file(file)
    #check if excel is loaded
    print(list_contracts[1])
    if not list_contracts[0].get('clientes'):
        return list_contracts
    
    #import contracts
    create_contracts = insert_contract_data(list_contracts, import_control)
    
    #check if excel is loaded
    if isinstance(create_contracts, tuple):
        return list_contracts
    
    import_control.status="Pronto para Importar"
    db.session.commit()
    return jsonify({"success": True, "message": "Imported to Stage finish"}), 201

@contracts.route('/home')
def home():
    return render_template('contracts/home.html')
