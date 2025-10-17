# tests/test_api_keycloak.py

import os
import requests
import pytest

# --- Configuration et Authentification (Étape 4) ---

# Récupération des variables d'environnement
KEYCLOAK_URL = os.environ.get('KEYCLOAK_URL')
KC_ADMIN_USER = os.environ.get('KC_ADMIN_USER')
KC_ADMIN_PASSWORD = os.environ.get('KC_ADMIN_PASSWORD')
KEYCLOAK_API_CLIENT_SECRET = os.environ.get('KEYCLOAK_API_CLIENT_SECRET')
TARGET_REALM = os.environ.get('TARGET_REALM')

# Le jeton d'accès administrateur est stocké ici après l'authentification
ADMIN_TOKEN = None
BASE_ADMIN_URL = f"{KEYCLOAK_URL}/admin/realms"

# Fonction d'authentification pour obtenir le jeton administrateur
def get_admin_token():
    global ADMIN_TOKEN
    
    # Vérifie si le jeton est déjà récupéré
    if ADMIN_TOKEN:
        return ADMIN_TOKEN
    
    # Endpoint pour le jeton Admin du realm master
    token_url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    
    data = {
        'client_id': 'admin-cli',
        'username': KC_ADMIN_USER,
        'password': KC_ADMIN_PASSWORD,
        'grant_type': 'password'
    }
    
    try:
        response = requests.post(token_url, data=data, timeout=10)
        response.raise_for_status() 
        
        token_data = response.json()
        ADMIN_TOKEN = token_data.get('access_token')
        
        if not ADMIN_TOKEN:
            pytest.fail("Token non trouvé dans la réponse d'authentification.")
        
        return ADMIN_TOKEN
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Échec de l'authentification Keycloak: {e}")


# Fixture Pytest pour fournir les headers d'autorisation aux tests
@pytest.fixture(scope="module")
def admin_headers():
    token = get_admin_token()
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

def get_service_account_token():
    """Tente d'obtenir un jeton d'accès pour le compte de service."""
    token_url = f"{KEYCLOAK_URL}/realms/{TARGET_REALM}/protocol/openid-connect/token"

    data = {
        'client_id': 'api-service-client',
        'client_secret': KEYCLOAK_API_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }

    try:
        response = requests.post(token_url, data=data, timeout=10)
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Erreur de connexion lors de la requête de jeton: {e}")

    # Si le statut n'est pas 200, nous renvoyons une erreur explicite
    if response.status_code != 200:
        pytest.fail(
            f"Échec de l'obtention du jeton (401/403). Statut: {response.status_code}. "
            f"Réponse: {response.text}"
        )

    # Si le statut est 200, nous vérifions le contenu
    try:
        response_json = response.json()
    except json.JSONDecodeError:
        pytest.fail(f"Réponse JSON invalide du serveur. Réponse: {response.text}")

    if 'access_token' not in response_json:
        pytest.fail("Le jeton d'accès est manquant dans la réponse JSON.")
    
    return response_json['access_token']

# --- Scénarios de Test (Étape 5) ---

def test_01_keycloak_is_reachable():
    """Vérifie que l'URL de base répond."""
    try:
        response = requests.get(KEYCLOAK_URL, timeout=5)
        assert response.status_code < 500, f"Le service Keycloak a retourné une erreur: {response.status_code}"
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Keycloak est injoignable: {e}")

def test_02_target_realm_exists(admin_headers):
    """Vérifie que le realm cible a été créé et est accessible via l'API Admin."""
    realm_url = f"{BASE_ADMIN_URL}/{TARGET_REALM}"
    response = requests.get(realm_url, headers=admin_headers)
    
    assert response.status_code == 200, f"Le Realm '{TARGET_REALM}' est introuvable (Status: {response.status_code})"
    
    # Validation d'un attribut de configuration critique
    realm_config = response.json()
    assert realm_config.get('enabled') is True, "Le Realm n'est pas activé."


def test_03_critical_client_is_present(admin_headers):
    """Vérifie qu'un client applicatif essentiel est présent et configuré."""
    client_name = "mon-client-applicatif" # ID du client à vérifier
    clients_url = f"{BASE_ADMIN_URL}/{TARGET_REALM}/clients"
    
    response = requests.get(clients_url, headers=admin_headers)
    assert response.status_code == 200, "Échec de l'accès à la liste des clients."
    
    clients = response.json()
    
    # Recherche du client par son ID
    found_client = next((c for c in clients if c.get('clientId') == client_name), None)
    
    assert found_client is not None, f"Le client critique '{client_name}' est manquant."
    
    # Vous pouvez ajouter ici des assertions sur le type d'accès, les redirections, etc.
    assert found_client.get('publicClient') is False, "Le client doit être confidentiel (non public)."


def test_04_list_clients_via_admin_api():
    """
    Test 04 exécute sa propre logique pour obtenir le jeton et tester l'API Admin.
    """
    # Étape 1 : Obtenir le jeton de manière indépendante
    access_token = get_service_account_token()

    # Étape 2 : Appeler l'API Admin
    clients_url = f"{KEYCLOAK_URL}/admin/realms/{TARGET_REALM}/clients"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(clients_url, headers=headers, timeout=10)

    # 1. Vérification du statut : 200 OK
    # Si le test échoue ici avec 403 Forbidden, le rôle 'view-clients' est manquant !
    assert response.status_code == 200, (
        f"Échec de l'accès à l'API Admin (Rôles ou URL incorrects). Statut: {response.status_code}. "
        f"Réponse: {response.text}"
    )

    clients_list = response.json()
    
    # 2. Vérification du contenu
    assert isinstance(clients_list, list), "La réponse n'est pas une liste de clients."
    assert len(clients_list) > 0, "La liste des clients est vide (inattendu)."

    # 3. Vérification que le client testé est présent (facultatif mais recommandé)
    client_ids = [client['clientId'] for client in clients_list]
    expected_clients = ['api-service-client', 'realm-management', 'account'] 

    for client_id in expected_clients:
        assert client_id in client_ids, f"Le client essentiel '{client_id}' n'a pas été trouvé."
