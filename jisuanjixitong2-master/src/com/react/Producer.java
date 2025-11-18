package com.react;

import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class Producer implements Runnable{

    public int picPosX;
    public int picPosY;
    public int picWidth;
    public int picHeight;
    public int produceSpeed;
    private Buffer buffer;
    public MyProgressBar myProgressBar;

    public String urlPath;

    public JButton onOrOff;



    private  int MIN_PROGRESS = 0;
    private  int MAX_PROGRESS = 100;
    private  int currentProgress = MIN_PROGRESS;
    public boolean isPause = true;

    @Override
    public void run() {
        while(true){
            try {
                Thread.sleep(produceSpeed);
                if(!isPause){
                    currentProgress++;
                    // 当生产者完成依次生产时
                    if (currentProgress >= MAX_PROGRESS) {
                        // 缓存区+1
                        buffer.produceAGood();
                        // 重新生产一个新的商品
                        currentProgress = 0;
                    }else {
                        // 采用进度条显示生产商品的过程
                        myProgressBar.getProgressBar().setValue(currentProgress);
                    }
                }
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
        }
    }

    public Producer(){
        myProgressBar = new MyProgressBar();
        produceSpeed = 30;
        initButton();
    }

    public Producer(Buffer buffer, String urlPath)
    {
        this.buffer = buffer;
        this.urlPath = urlPath;
        produceSpeed = 30;
        myProgressBar = new MyProgressBar();
        initButton();
    }

    public Producer(Buffer buffer, String urlPath, int picPosX, int picPosY, int picWidth, int picHeight,int produceSpeed) {
        this.urlPath = urlPath;
        this.picPosX = picPosX;
        this.picPosY = picPosY;
        this.picWidth = picWidth;
        this.picHeight = picHeight;
        this.produceSpeed = produceSpeed;
        this.buffer = buffer;
        myProgressBar = new MyProgressBar();

        initButton();
    }

    // 初始化生产者的按钮相关信息
    public void initButton(){
        onOrOff = new JButton();

        onOrOff.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                if(onOrOff.getLabel().equals("On")){
//                    getStart();
                    isPause = false;
                    onOrOff.setLabel("Off");
                }else {
//                    getStop();
                    isPause = true;
                    onOrOff.setLabel("On");
                }
            }
        });

    }

}
