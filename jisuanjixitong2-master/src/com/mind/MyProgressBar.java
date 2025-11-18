package com.mind;

import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class MyProgressBar extends Thread{

    private String BarName;

    private int posx;

    private int posy;

    private  int MIN_PROGRESS = 0;

    private  int MAX_PROGRESS = 100;

    private  int currentProgress = MIN_PROGRESS;

    // 创建一个进度条
    private JProgressBar progressBar;

    private Timer timer;

    public boolean isPause = true;
    public boolean isFull = false;

    public MyProgressBar(){
        progressBar = new JProgressBar();

        // 设置进度的 最小值 和 最大值
        progressBar.setMinimum(MIN_PROGRESS);
        progressBar.setMaximum(MAX_PROGRESS);

        // 设置进度条方向(竖直)
        progressBar.setOrientation(SwingConstants.VERTICAL);

        // 设置当前进度值
        progressBar.setValue(currentProgress);

        // 绘制百分比文本(进度条中间显示的百分数)
        progressBar.setStringPainted(true);

        // 模拟延时操作进度, 每隔 0.1 秒更新进度
        timer = new Timer(75, new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {

                currentProgress++;
                // 已完成该进程
                if (currentProgress > MAX_PROGRESS) {
                    isFull = true;
                    return;
                }

                progressBar.setValue(currentProgress);
            }

        });
    }

    public MyProgressBar(String barName, int posx, int posy){
        // 设置进度条的名称
        this.BarName = barName;

        // 设置资源给到该进度条时，学生（CPU）图片应该移动到哪里
        this.posx = posx;
        this.posy = posy;

        progressBar = new JProgressBar();

        // 设置进度的 最小值 和 最大值
        progressBar.setMinimum(MIN_PROGRESS);
        progressBar.setMaximum(MAX_PROGRESS);

        // 设置进度条方向(竖直)
        progressBar.setOrientation(SwingConstants.VERTICAL);

        // 设置当前进度值
        progressBar.setValue(currentProgress);

        // 绘制百分比文本(进度条中间显示的百分数)
        progressBar.setStringPainted(true);

        // 模拟延时操作进度, 每隔 0.1 秒更新进度
        timer = new Timer(75, new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {

                currentProgress++;
                // 已完成该进程
                if (currentProgress > MAX_PROGRESS) {
                    isFull = true;
                    return;
                }

                progressBar.setValue(currentProgress);
            }

        });
    }

    public JProgressBar getProgressBar() {
        progressBar = new JProgressBar();

        // 设置进度的 最小值 和 最大值
        progressBar.setMinimum(MIN_PROGRESS);
        progressBar.setMaximum(MAX_PROGRESS);

        // 设置进度条方向(竖直)
        progressBar.setOrientation(SwingConstants.VERTICAL);

        // 设置当前进度值
        progressBar.setValue(currentProgress);

        // 绘制百分比文本(进度条中间显示的百分数)
        progressBar.setStringPainted(true);

        return progressBar;

    }

    // 该进程获得CPU 资源
    public void getStart(){
//        if(isPause)
//            return;

        timer.start();
    }

    // 该进程给出资源
    public void getStop(){
        timer.stop();
    }

    public void restart(){
        this.currentProgress = MIN_PROGRESS;
        isPause = true;
        isFull = false;
        this.progressBar.setValue(currentProgress);

    }

    public String getBarName(){
        return this.BarName;
    }

    public int getPosx(){
        return this.posx;
    }

    public int getPosy(){
        return this.posy;
    }
}
