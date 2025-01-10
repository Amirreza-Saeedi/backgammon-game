from router import Router
import router as rt

if __name__ == '__main__':
    router = Router(rt.R2_PORT, rt.R3_PORT)
    router.start()
    
