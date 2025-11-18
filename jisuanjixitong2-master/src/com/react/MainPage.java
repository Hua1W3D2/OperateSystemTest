package com.react;

import javax.swing.*;
import java.awt.*;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

public class MainPage {
    public JFrame PageGUI;

    private Buffer buffer;

    // 监听器，用于监听Java Bean 属性的变化
    PropertyChangeListener consumerListener;

    // 餐桌的Panel
    JPanel dishTablePanel = new JPanel();

    // 商品（生产者生产的商品）的集合
    List<JLabel> consumerLabelList;

    // 无参构造方法
    public MainPage(){
        buffer = new Buffer();
        consumerLabelList = new ArrayList<>();
    }

    // 主界面有参构造方法
    public MainPage(Buffer buffer){
        this.buffer = buffer;
        consumerLabelList = new ArrayList<>();
    }

    public void AllInit(){
        // 界面初始化
        frameInit();
        // 初始化监听器
        someListenerInit();
        // 生产者与消费者相关信息的初始化
        ProducerAndConsumerInit();
        // 图片的初始化
        ImgsInit();
        // 餐桌的初始化
        drawDishOnTable();
    }

    // Producer And Consumer Init
    public void ProducerAndConsumerInit(){
        // 生产者进度条的初始位置
        int ProgressBarPosX = 5;
        // 生产者控制按钮的位置
        int ProducerControllBtnPosX = 50;
        for(int i=0;i<buffer.producerList.size();i++)
        {
            // 准备生产者的进度条
            Producer producer = buffer.producerList.get(i);
            JPanel panel = new JPanel();
            panel.setSize(150,30);
            panel.setLocation(ProgressBarPosX,135);
            ProgressBarPosX += 245;
            panel.add(producer.myProgressBar.getProgressBar());
            PageGUI.getContentPane().add(panel);

            // 准备生产者的按钮
            producer.onOrOff.setLabel("On");
            producer.onOrOff.setSize(60,30);
            producer.onOrOff.setLocation(ProducerControllBtnPosX,170);
            ProducerControllBtnPosX += 245;
            PageGUI.getContentPane().add(producer.onOrOff);
        }

        // 消费者控制按钮的位置
        int ConsumerControllBtnPosX = 90;
        for(int i=0;i<buffer.consumerList.size();i++){
            // 准备消费者的按钮
            Consumer consumer = buffer.consumerList.get(i);
            consumer.onOrOff.setLabel("On");
            consumer.onOrOff.setSize(60,30);
            consumer.onOrOff.setLocation(ConsumerControllBtnPosX,670);
            ConsumerControllBtnPosX += 235;
            PageGUI.getContentPane().add(consumer.onOrOff);

            // 添加移动监听器，实时让界面刷新
            consumer.addPropertyChangeListener(consumerListener);

            // 添加显示消费者图片的label
            URL url = Main.class.getResource(consumer.urlPath);
            JLabel label = getImg(consumer.picPosX, consumer.picPosY, consumer.picWidth, consumer.picHeight, url);
            consumerLabelList.add(label);
            PageGUI.getContentPane().add(label);
        }
    }

    // 显示餐桌商品（显示缓存器产品）
    public void drawDishOnTable(){
        dishTablePanel.removeAll();

        URL url = Main.class.getResource("/imgs/beff.png");
        int posx = 5;
        for(int i=0;i<buffer.getGoodNum();i++)
        {
            JLabel dish = getImg(posx, 5, 70 ,70, url);
            posx += 75;
            dishTablePanel.add(dish);
        }

        PageGUI.repaint();
    }

    // 监听器初始化
    public void someListenerInit(){
        PropertyChangeListener bufferListener = new PropertyChangeListener() {
            @Override
            public void propertyChange(PropertyChangeEvent evt) {
                drawDishOnTable();
            }
        };

        // 缓存器监听器
        buffer.addPropertyChangeListener(bufferListener);

        // 消费者监听器
        consumerListener = new PropertyChangeListener() {
            @Override
            public void propertyChange(PropertyChangeEvent evt) {
                if(evt.getPropertyName().equals("Waiter-1")){
                    JLabel label = consumerLabelList.get(0);
                    label.setLocation(label.getX(),(int)evt.getNewValue());
                }
                if(evt.getPropertyName().equals("Waiter-2")){
                    JLabel label = consumerLabelList.get(1);
                    label.setLocation(label.getX(),(int)evt.getNewValue());
                }
                if(evt.getPropertyName().equals("Waiter-3")){
                    JLabel label = consumerLabelList.get(2);
                    label.setLocation(label.getX(),(int)evt.getNewValue());
                }
                PageGUI.repaint();
            }
        };
    }

    // 初始化页面相关信息
    public void frameInit(){
        PageGUI = new JFrame("生产者与消费者演示");
        PageGUI.setSize(750,750);
        PageGUI.setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
        PageGUI.setLayout(null);

        dishTablePanel.setBorder(BorderFactory.createLineBorder(Color.darkGray,2));
        dishTablePanel.setSize(650,80);
        dishTablePanel.setLocation(30,250);
        dishTablePanel.setLayout(null);
        PageGUI.getContentPane().add(dishTablePanel);
    }

    // 初始化页面图片相关信息
    public void ImgsInit(){
        // 厨师相关的图片初始化
        for (int i = 0; i < buffer.producerList.size(); i++) {
            Producer producer = buffer.producerList.get(i);
            URL url = Main.class.getResource(producer.urlPath);
            PageGUI.getContentPane().add(getImg(producer.picPosX,producer.picPosY,producer.picWidth,producer.picHeight,url));
        }
    }

    // 将图片缩放到指定大小
    public JLabel getImg(int posx, int posy, int width, int height, URL url){
        JLabel imgLabel = new JLabel();
        ImageIcon img1 = new ImageIcon(url);

        Image imageTmp = img1.getImage();
        imageTmp = imageTmp.getScaledInstance(width,height,Image.SCALE_DEFAULT);

        img1.setImage(imageTmp);

        imgLabel.setIcon(img1);
        imgLabel.setBounds(posx, posy, img1.getIconWidth(), img1.getIconHeight());

        return imgLabel;
    }

}
