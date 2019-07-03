import os 

def clean_ports():
    """
        Limpia varios puertos asociados a la ejecución del proyecto
    """

    print('Clenaning ports...')
    os.system('sudo fuser -k 5000/tcp')
    os.system('sudo fuser -k 20000/tcp')
    os.system('sudo fuser -k 8095/tcp')
    os.system('sudo fuser -k 8096/tcp')
    os.system('sudo fuser -k 8097/tcp')
    os.system('sudo fuser -k 8098/tcp')
    os.system('sudo fuser -k 8000/tcp')
    os.system('sudo fuser -k 8001/tcp')

def launch():
    """
        Lanza a ejecución el proyecto
    """
    os.system('pade start-runtime --port 20000 agents.py --no_pade_web')


if __name__ == '__main__':
    clean_ports()
    launch()