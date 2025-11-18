package com.react;

import javax.swing.*;
import javax.swing.border.BevelBorder;
import javax.swing.border.Border;
import java.awt.*;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

public class Main {

    public static void main(String[] args) {
        Buffer buffer = new Buffer();

        Producer producer1 = new Producer(buffer, "/imgs/cooker2.jpeg", 25, 25, 110, 110,30);
        Producer producer2 = new Producer(buffer,"/imgs/cooker2.jpeg",270,25,110,110,35);
        Producer producer3 = new Producer(buffer,"/imgs/cooker2.jpeg",520,25,110,110,25);

        Consumer consumer1 = new Consumer(buffer,"/imgs/waiter.jpeg",75,550,90,112,15);
        Consumer consumer2 = new Consumer(buffer,"/imgs/waiter.jpeg",310,550,90,112,16);
        Consumer consumer3 = new Consumer(buffer,"/imgs/waiter.jpeg",550,550,90,112,17);

        Thread t1 = new Thread(producer1,"Cooker-1");
        Thread t2 = new Thread(producer2,"Cooker-2");
        Thread t3 = new Thread(producer3,"Cooker-3");
        Thread t4 = new Thread(consumer1,"Waiter-1");
        Thread t5 = new Thread(consumer2,"Waiter-2");
        Thread t6 = new Thread(consumer3,"Waiter-3");

        t1.start();
        t2.start();
        t3.start();
        t4.start();
        t5.start();
        t6.start();

        List<Producer> producer_list = new ArrayList<>();
        producer_list.add(producer1);
        producer_list.add(producer2);
        producer_list.add(producer3);

        List<Consumer> consumer_list = new ArrayList<>();
        consumer_list.add(consumer1);
        consumer_list.add(consumer2);
        consumer_list.add(consumer3);

        buffer.producerList = producer_list;
        buffer.consumerList =consumer_list;


        MainPage mainPage = new MainPage(buffer);

        mainPage.AllInit();

        mainPage.PageGUI.setVisible(true);

    }
}
