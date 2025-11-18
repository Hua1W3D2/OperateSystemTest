package com.mind;

public class Consumer implements Runnable{

    // 控制消费者状态（消费/暂停）
    public boolean isPause = false;

    public Buffer buffer;

    @Override
    public void run() {
        while(true){
            try {
                Thread.sleep(3000);
                if(!isPause){
                    // 缓存区商品-1
                    buffer.consumeAGood();
                }
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
        }
    }

    public Consumer(){
    }

    public Consumer(Buffer buffer){
        this.buffer = buffer;
    }
}
