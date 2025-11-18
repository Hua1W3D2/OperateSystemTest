package com.mind;

public class Producer implements Runnable{

    private Buffer buffer;
    public boolean isPause = false;

    @Override
    public void run() {
        while(true){
            try {
                Thread.sleep(1000);
                if(!isPause){
                    // 缓存区+1
                    buffer.produceAGood();
                }
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
        }
    }

    public Producer(){
    }

    public Producer(Buffer buffer)
    {
        this.buffer = buffer;
    }

}
