package com.mind;

public class Main {
    public static void  main(String[] args) {
        Buffer buffer = new Buffer();

        Producer producer1 = new Producer(buffer);
        Producer producer2 = new Producer(buffer);
        Producer producer3 = new Producer(buffer);
        Consumer consumer1 = new Consumer(buffer);
        Consumer consumer2 = new Consumer(buffer);
        Consumer consumer3 = new Consumer(buffer);

        Thread t1 = new Thread(producer1,"Producer_1");
        Thread t2 = new Thread(producer2,"Producer_2");
        Thread t3 = new Thread(producer3,"Producer_3");
        Thread t4 = new Thread(consumer1,"Consumer_1");
        Thread t5 = new Thread(consumer2,"Consumer_2");
        Thread t6 = new Thread(consumer3,"Consumer_3");

        t1.start();
        t2.start();
        t3.start();
        t4.start();
        t5.start();
        t6.start();
    }
}
