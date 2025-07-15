import datetime
import random

def es_primo(n: int) -> bool:
    """Determina si un número es primo."""
    if n <= 1:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def solicitar_numero() -> int:
    """Solicita al usuario un número entero y lo devuelve."""
    while True:
        entrada = input("Ingrese un número para verificar si es primo: ")
        try:
            return int(entrada)
        except ValueError:
            print("❌ Entrada inválida. Por favor, ingrese un número entero.")

def verificar_primo():
    """Verifica si el número ingresado es primo e informa al usuario."""
    numero = solicitar_numero()
    if es_primo(numero):
        print(f"✅ {numero} es un número primo.")
    else:
        print(f"❌ {numero} no es un número primo.")

def mostrar_menu():
    """Muestra el menú principal."""
    print("\n--- MENÚ PRINCIPAL ---")
    print("1. Mostrar frase motivacional")
    print("2. Mostrar fecha actual")
    print("3. Salir")

def obtener_frase_motivacional() -> str:
    frases = [
        "¡Tú puedes lograr todo lo que te propongas! 💪",
        "Cada día es una nueva oportunidad para ser mejor. 🌟",
        "La perseverancia es la clave del éxito. 🚀",
        "No te rindas, el éxito está más cerca de lo que piensas. 🌈",
        "Cree en ti mismo y todo será posible. ✨"
    ]
    return random.choice(frases)

def mostrar_fecha_actual() -> str:
    return datetime.datetime.now().strftime("%d/%m/%Y")

def menu_interactivo():
    """Muestra un menú interactivo con opciones para el usuario."""
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción (1-3): ")

        if opcion == "1":
            print(f"\n📝 Frase motivacional: {obtener_frase_motivacional()}")
        elif opcion == "2":
            print(f"\n📅 Fecha actual: {mostrar_fecha_actual()}")
        elif opcion == "3":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida. Por favor, elige 1, 2 o 3.")

def main():
    """Función principal del programa."""
    print("🎉 Bienvenido al programa de ejercicios.")
    verificar_primo()
    menu_interactivo()
    print("🙏 Gracias por participar. ¡Hasta la próxima!")

if __name__ == "__main__":
    main()
