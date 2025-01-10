from router import Router
import router as rt

if __name__ == '__main__':
    router = Router(rt.R1_PORT, rt.R2_PORT)
    router.start()
    
