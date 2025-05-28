from haversine import haversine

ponto1 = (-23.3045,	-51.1696) # (lat, lon)
ponto2 = (-23.3045,	-51.16920832)

distancia = haversine(ponto1, ponto2)*1000

print(f'{distancia}')

