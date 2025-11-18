package com.react;

import javax.swing.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

// 进度条，模拟生产者生产过程
public class MyProgressBar extends Thread{

    private  int MIN_PROGRESS = 0;
    private  int MAX_PROGRESS = 100;
    private  int currentProgress = MIN_PROGRESS;

    public boolean isPause = true;
    public boolean isFull = false;

    public JProgressBar getProgressBar() {
        return progressBar;
    }

    private JProgressBar progressBar;

    MyProgressBar(){
        prepareBar();
    }

    private void prepareBar(){
        progressBar = new JProgressBar();

        // 设置进度的 最小值 和 最大值
        progressBar.setMinimum(MIN_PROGRESS);
        progressBar.setMaximum(MAX_PROGRESS);

        // 设置当前进度值
        progressBar.setValue(currentProgress);

        // 绘制百分比文本(进度条中间显示的百分数)
        progressBar.setStringPainted(true);
    }

}
