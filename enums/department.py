from enum import StrEnum


class DepartmentName(StrEnum):
    """
    Enumeration of company departments with descriptive names.

    Each member represents a department with its official name.
    These values can be modified if needed, for example, if the naming
    of a department changes.

    Usage:
        >>> DepartmentName.RH
        <DepartmentName.RH: 'Recursos humanos'>
        >>> str(DepartmentName.RH)
        'Recursos humanos'
    """

    ADM_GRUPOS = "Adm grupos"
    ATD_CLIENTE = "Atendimento ao cliente"
    BOAS_VINDAS = "Boas vindas"
    COBRANCA = "Cobrança"
    CONTABILIDADE = "Contabilidade"
    CONTROLADORIA = "Controladoria"
    CREDITO = "Crédito"
    FACILITIES = "Facilities"
    FINANCEIRO = "Financeiro"
    JURIDICO = "Jurídico"
    OUVIDORIA = "Ouvidoria"
    RECOMPRA = "Recompra"
    RH = "Recursos humanos"
    GENTEGESTAO = "Gente & gestão"
    REATIVACAO = "Reativação"
    SEGUROS = "Seguros"
    TI = "Tecnologia"
    VENDAS = "Vendas"
    VENDAS_ONLINE = "Vendas online"
    SUCESSO_DO_CLIENTE = "Sucesso do cliente"
    DADOS = "Dados"


class DepartmentFolderNumber(StrEnum):
    """
    Enumeration of numeric codes corresponding to each department.

    Each member represents the folder number or code associated with a department.
    The values can be modified if the numbering changes in the system or folder organization.

    Usage:
        >>> DepartmentFolderNumber.RH
        <DepartmentFolderNumber.RH: '13'>
        >>> str(DepartmentFolderNumber.RH)
        '13'
    """

    ADM_GRUPOS = "01"
    ATD_CLIENTE = "02"
    BOAS_VINDAS = "03"
    COBRANCA = "04"
    CONTABILIDADE = "05"
    CONTROLADORIA = "06"
    CREDITO = "07"
    FACILITIES = "08"
    FINANCEIRO = "09"
    JURIDICO = "10"
    OUVIDORIA = "11"
    RECOMPRA = "12"
    RH = "13"
    REATIVACAO = "14"
    SEGUROS = "15"
    TI = "16"
    VENDAS = "17"
    VENDAS_ONLINE = "18"
    SUCESSO_DO_CLIENTE = "19"
    DADOS = "20"
