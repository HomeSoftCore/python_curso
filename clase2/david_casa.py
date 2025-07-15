from typing import List


# ----------------------- Ejercicio 1: Clase Heroe -----------------------

class Heroe:
    def __init__(self, nombre: str, genero: str, identidad_secreta: str, poder: str):
        self.nombre = nombre
        self.genero = genero
        self.identidad_secreta = identidad_secreta
        self.poder = poder

    def presentar(self) -> None:
        print(f"🦸‍♂️ Soy {self.nombre}, tengo el poder de {self.poder}, "
              f"y mi identidad secreta es {self.identidad_secreta}.")

    def to_json(self) -> dict:
        return {
            "nombre": self.nombre,
            "genero": self.genero,
            "identidad_secreta": self.identidad_secreta,
            "poder": self.poder
        }


# ----------------------- Ejercicio 2: Clase Pelicula -----------------------

class Pelicula:
    def __init__(self, titulo: str, director: str, anio: int):
        self.titulo = titulo
        self.director = director
        self.anio = anio

    def mostrar_info(self) -> None:
        print(f"🎬 {self.titulo} ({self.anio}), dirigido por {self.director}.")


# ----------------------- Ejercicio 3: Trivia con POO -----------------------

class Pregunta:
    def __init__(self, enunciado: str, opciones: List[str], respuesta_correcta: str):
        self.enunciado = enunciado
        self.opciones = opciones
        self.respuesta_correcta = respuesta_correcta

    def mostrar(self) -> None:
        print(f"\n❓ {self.enunciado}")
        for idx, opcion in enumerate(self.opciones, start=1):
            print(f"  {idx}. {opcion}")

    def verificar_respuesta(self, respuesta_usuario: str) -> bool:
        try:
            indice = int(respuesta_usuario) - 1
            return self.opciones[indice].strip().lower() == self.respuesta_correcta.strip().lower()
        except (ValueError, IndexError):
            return False


class Trivia:
    def __init__(self):
        self.preguntas: List[Pregunta] = []

    def agregar_pregunta(self, pregunta: Pregunta) -> None:
        self.preguntas.append(pregunta)

    def iniciar(self) -> None:
        print("\n🧠 Bienvenido a la Trivia. ¡Buena suerte!\n")
        for pregunta in self.preguntas:
            pregunta.mostrar()
            respuesta = input("👉 Ingresa el número de la opción correcta: ")
            if pregunta.verificar_respuesta(respuesta):
                print("✅ ¡Respuesta correcta!")
            else:
                print(f"❌ Respuesta incorrecta. La correcta era: {pregunta.respuesta_correcta}")


# ----------------------- Bloque Principal -----------------------

def main():
    print("************ Ejercicio 1: Clase Heroe ************")
    heroe = Heroe("Superman", "Masculino", "Clark Kent", "Super fuerza")
    heroe.presentar()
    heroe.poder = "Volar"
    heroe.presentar()
    print("📦 Héroe en formato JSON:", heroe.to_json())

    print("\n************ Ejercicio 2: Lista de Películas ************")
    peliculas = [
        Pelicula("Toy Story", "John Lasseter", 1995),
        Pelicula("Forrest Gump", "Robert Zemeckis", 1994),
        Pelicula("Insidious", "James Wan", 2010),
        Pelicula("El Padrino", "Francis Ford Coppola", 1972),
    ]
    for pelicula in peliculas:
        pelicula.mostrar_info()

    print("\n************ Ejercicio 3: Trivia ************")
    trivia = Trivia()
    trivia.agregar_pregunta(Pregunta(
        "¿Cuál es la capital de Francia?",
        ["Berlín", "Madrid", "París", "Roma"],
        "París"
    ))
    trivia.agregar_pregunta(Pregunta(
        "¿Cuál es el océano más grande del mundo?",
        ["Atlántico", "Índico", "Ártico", "Pacífico"],
        "Pacífico"
    ))
    trivia.agregar_pregunta(Pregunta(
        "¿Quién escribió 'Cien años de soledad'?",
        ["Gabriel García Márquez", "Mario Vargas Llosa", "Jorge Luis Borges", "Pablo Neruda"],
        "Gabriel García Márquez"
    ))
    trivia.iniciar()

    print("\n🎉 ¡Gracias por usar el programa!")


if __name__ == "__main__":
    main()
