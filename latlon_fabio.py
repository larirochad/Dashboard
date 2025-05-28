import math

def calcular_distancia(lat1, lon1, lat2, lon2):
    # Raio da Terra em metros
    R = 6371000

    # Converter graus para radianos
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Fórmula de Haversine
    a = math.sin(delta_phi / 2) * math.sin(delta_phi / 2) + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2) * math.sin(delta_lambda / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c

    return d  # Distância em metros


#Exemplo de uso
lat1 = -23.324132821728362  # Latitude do ponto 1
lon1 = -51.170532021961556  # Longitude do ponto 1
lat2 = -23.3413237  # Latitude do ponto 2
lon2 = -51.1856072  # Longitude do ponto 2

distancia = calcular_distancia(lat1, lon1, lat2, lon2)
print(f"A distância entre os pontos é {distancia:.2f} metros") 
