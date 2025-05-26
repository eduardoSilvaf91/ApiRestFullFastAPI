import re

def validate_cpf(cpf: str):
    """Validação simples de CPF (pode ser implementada a validação real)"""
    cpf = remove_special_characters(cpf)
    
    if len(cpf) != 11 or not cpf.isdigit():
        return False
    return True

def remove_special_characters(cpf: str):
    """Remove caracteres especiais de um CPF"""
    return re.sub(r'[^0-9]', '', cpf)