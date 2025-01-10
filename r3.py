from router import Router
import router as rt

if __name__ == '__main__':
    router = Router(rt.R3_PORT, 10_000)
    router.start()
    
