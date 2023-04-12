
import concurrent.futures
from multiprocessing import cpu_count
from random import shuffle
from time import time
from itertools import combinations


class Baralho:

    def __init__(self):
        self.contruir_baralho()
        self.embaralhar()

    def contruir_baralho(self):
        VALORES = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        NAIPES = ["c", "d", "h", "s"]
        self.carta = {}
        for (idx_v, valor) in enumerate(VALORES):
            for (idx_n, naipe) in  enumerate(NAIPES):
                self.carta[valor+naipe] ={
                    "valor": idx_v,
                    "naipe": naipe
                }
        self.forca_ref = [(len(VALORES)**k) for k in range(6,-1,-1)]
        self.baralho = list(self.carta.keys())

    def embaralhar(self):
        shuffle(self.baralho)
        self.topo = 0
        return self.baralho

    def remover(self, carta: str):
        if carta in self.baralho:
            self.baralho.remove(carta)

    def simular(self, quantidade: int=1):
        simul = self.baralho[self.topo:]
        shuffle(simul)
        return simul[:quantidade]

    def dar_cartas(self, quantidade: int=1 ):
        fim = min(self.topo + quantidade, len(self.baralho))
        cartas_distribuidas = self.baralho[self.topo:fim]
        self.topo = fim
        return cartas_distribuidas

    def combinacoes_restantes(self, quantidade):
        return combinations(self.baralho[self.topo:], quantidade)

    def forca_combinacao(self, combinacao):
        if len(combinacao)<5:
            return 0
        combinacoes = combinations(combinacao,5)

        forca_max = 0
        caption_max = ""
        for comb in combinacoes:
            forca, caption = self.forca(comb)
            if forca > forca_max:
                forca_max, caption_max = forca, caption
        return forca_max, caption_max

    def idx_forca(self, *args):
        forca = 0
        for idx, arg in enumerate(args):
            forca+= arg* self.forca_ref[idx]
        return forca

    def forca(self, cartas):
        if len(cartas) != 5:
            return 0
        naipes = ""
        valores = []
        for carta in cartas:
            naipes += str(self.carta[carta]["naipe"])
            valores.append(self.carta[carta]["valor"])

        flush = True
        for naipe in naipes:
            flush = flush and naipe == naipes[0]
        valores.sort(reverse=True)

        dobras = [[], [], [], []]
        idx_dobra = 0
        for idx_valor in range(1, len(valores)):
            if valores[idx_valor] == valores[idx_valor -1]:
                idx_dobra += 1
            else:
                dobras[idx_dobra].append(valores[idx_valor-1])
                idx_dobra = 0
        dobras[idx_dobra].append(valores[-1])

        sequencia = len(dobras[0]) == 5 and valores[0] - valores[4] == 4

        if sequencia and flush:
            forca = self.idx_forca(8,valores[0])
            caption = "Straight Flush"
        elif dobras[3]:
            forca = self.idx_forca(7, dobras[3][0],dobras[0][0])
            caption = "Quadra"
        elif dobras[2] and dobras[1]:
            forca = self.idx_forca(6, dobras[2][0],dobras[1][0])
            caption = "Full House"
        elif flush:
            forca = self.idx_forca(5,  dobras[0][0], dobras[0][1], dobras[0][2], dobras[0][3], dobras[0][4])
            caption = "Flush"
        elif sequencia:
            forca = self.idx_forca(4, valores[0])
            caption = "Sequencia"
        elif dobras[2]:
            forca = self.idx_forca(3, dobras[2][0], dobras[0][0], dobras[0][1])
            caption = "Trinca"
        elif len(dobras[1])==2:
            forca = self.idx_forca(2, dobras[1][0], dobras[1][1], dobras[0][0])
            caption = "Dois Pares"
        elif dobras[1]:
            forca = self.idx_forca(1, dobras[1][0], *dobras[0])
            caption = "Par"
        else:
            forca = self.idx_forca(0, dobras[0][0], dobras[0][1], dobras[0][2], dobras[0][3], dobras[0][4])
            caption = "Carta Alta"
        caption += "= " + str(cartas)
        return forca, caption


class Equidade:

    def __init__(self, lista_maos, board, iteracoes: int = 15000):
        self.lista_maos = lista_maos
        self.board = board
        self.iteracoes = iteracoes

    def __repartir(self, n, q):
        return  [n//q + int((n % q)>((n-1-i) % q)) for i in range(q)]

    def calcular_equidade_single(self, iteracoes: int):
        agora = time()
        resultados = []
        br = Baralho()
        for mao in self.lista_maos:
            resultados.append({"mao": mao,
                           "comb": [],
                           "eq_v": 0.0,
                           "eq_e": 0.0,
                           "forca": 0,
            })
            for carta in mao:
                br.remover(carta)
        for carta in self.board:
            br.remover(carta)
        for _ in range(iteracoes):
            board = self.board + br.simular(5-len(self.board))
            forca_vencedora = 0
            num_ganhadores = 0
            for result in resultados:
                result['comb'] = result['mao'] + board
                result['forca'], _ = br.forca_combinacao(result['comb'])
                if result['forca'] > forca_vencedora:
                    forca_vencedora = result['forca']
                    num_ganhadores = 1
                elif result['forca'] == forca_vencedora:
                    num_ganhadores += 1

            for result in resultados:
                if result['forca'] == forca_vencedora:
                    if num_ganhadores == 1:
                        result['eq_v'] += 1.0
                    else:
                        result['eq_e'] += 1.0/num_ganhadores

        tempo = max(time() - agora, 0.000001)
        veloc = iteracoes/tempo
        txt = f"TEMPO= {tempo:.1f}s\nVELOC= {veloc:.0f}hz:\n"
        txt += f"RESULTADOS APÓS {iteracoes} SIMULAÇÕES:\n\n"
        txt += f"BOARD {self.board}\n\n"
        for result in resultados:
            txt += f"{result['mao']}= {100*(result['eq_v']+result['eq_e'])/iteracoes:.2f}%"
            txt += f"\n\tvit= {100*result['eq_v']/iteracoes:.2f}%"
            txt += f"\n\temp= {100*result['eq_e']/iteracoes:.2f}%\n"
            del(result['comb'])
            del (result['forca'])
            result["iter"] = iteracoes
        return resultados, txt

    def calcular_equidade(self):
        agora = time()
        NUM_PROCESSOS = min(cpu_count(), self.iteracoes)
        divisao = self.iteracoes // NUM_PROCESSOS + 1
        resultados_simulacoes = []
        vetor_divisao = [divisao for _ in range(NUM_PROCESSOS)]

        with concurrent.futures.ProcessPoolExecutor() as executor:
            for _, resultado in zip(vetor_divisao, executor.map(self.calcular_equidade_single, vetor_divisao)):
                resultados_simulacoes.append(resultado[0])

        consolidado = {}
        iniciou_mao = False
        for result in resultados_simulacoes:
            if not iniciou_mao:
                for mao_res in result:
                    consolidado[str(mao_res["mao"])] = {'eq_v':mao_res['eq_v'],'eq_e': mao_res['eq_e'] }
                iniciou_mao = True
            else:
                for mao_res in result:
                    consolidado[str(mao_res["mao"])]['eq_v'] += mao_res['eq_v']
                    consolidado[str(mao_res["mao"])]['eq_e'] += mao_res['eq_e']

        tempo = max(time() - agora, 0.000001)
        veloc = self.iteracoes / tempo
        txt = f"TEMPO= {tempo:.1f}s:\n"
        txt += f"VELOC= {veloc:.0f}hz:\n"
        txt += f"RESULTADOS APÓS {self.iteracoes} SIMULAÇÕES em {NUM_PROCESSOS} núcleos:\n\n"
        txt += f"BOARD {self.board}\n"
        for chave, valor in consolidado.items():
            txt += f"\n{chave}= {100 * (valor['eq_v'] + valor['eq_e']) / self.iteracoes:.2f}%"
            txt += f"\n\tvit= {100 * valor['eq_v'] / self.iteracoes:.2f}%"
            txt += f"\n\temp= {100 * valor['eq_e'] / self.iteracoes:.2f}%\n"
        return {'results': consolidado, 'caption': txt}
