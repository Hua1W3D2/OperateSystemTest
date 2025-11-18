package com.react;


import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeSupport;

public class Consumer implements Runnable{

    public int picPosX;
    public int picPosY;
    public int picWidth;
    public int picHeight;
    public int consumeSpeed;
    private  int DEADLINE = 350;
    public String urlPath;
    public JButton onOrOff;
    PropertyChangeSupport listeners;



    // 控制消费者状态（消费/暂停）
    public boolean isPause = true;

    public Buffer buffer;


    @Override
    public void run() {
        while(true){
            try {
                Thread.sleep(consumeSpeed);
                if(!isPause){
                    picPosY--;
                    // 消费者完成一次消费
                    if (picPosY <= DEADLINE) {
                        // 缓存区商品-1
                        buffer.consumeAGood();
                        // 重置消费者位置
                        picPosY = 550;
                    }
                    // 更新消费者的位置
                    listeners.firePropertyChange(Thread.currentThread().getName(),picPosY+1,picPosY);
                }
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
        }
    }

    public Consumer(){
        initButton();
        consumeSpeed = 18;
        listeners = new PropertyChangeSupport(this);
    }

    public Consumer(Buffer buffer, String urlPath){
        this.buffer = buffer;
        this.urlPath = urlPath;
        consumeSpeed = 18;
        initButton();
        listeners = new PropertyChangeSupport(this);
    }

    public Consumer(Buffer buffer, String urlPath, int picPosX, int picPosY, int picWidth, int picHeight,int consumeSpeed) {
        this.urlPath = urlPath;
        this.picPosX = picPosX;
        this.picPosY = picPosY;
        this.picWidth = picWidth;
        this.picHeight = picHeight;
        this.consumeSpeed = consumeSpeed;
        this.buffer = buffer;

        initButton();
        listeners = new PropertyChangeSupport(this);
    }

    // 初始化消费者按钮的相关信息
    public void initButton(){
        onOrOff = new JButton();

        onOrOff.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                if(onOrOff.getLabel().equals("On")){
                    isPause = false;
                    onOrOff.setLabel("Off");
                }else {
                    isPause = true;
                    onOrOff.setLabel("On");
                }
            }
        });

    }

    public void addPropertyChangeListener(PropertyChangeListener listener){
        listeners.addPropertyChangeListener(listener);
    }
}
