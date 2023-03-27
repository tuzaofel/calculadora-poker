
from baralho import Equidade


def main():
    lista_maos = [["As", "Kd"], ["Qs", "Qd"]]
    board = ["Tc", "Js", "Kc"]
    eq = Equidade(lista_maos, board)
    resultados, texto = eq.calcular_equidade()
    print(texto)

if __name__ == '__main__':
    main()
