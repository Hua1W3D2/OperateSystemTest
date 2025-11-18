package com.mind;

import com.react.Consumer;
import com.react.Producer;

import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeSupport;
import java.util.List;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class Buffer {
    // 缓存区最大产品数
    private static final int MAX = 10;

    // 当前缓存区产品的个数
    private int GoodNum = 0;

    // 判断缓存区是否已经满了
    public boolean isFull = false;

    // 判断缓存区是否为空
    public boolean isEmpty = true;

    // 锁
    private final Lock lock = new ReentrantLock();

    // 缓存区满的条件变量
    private final Condition full = lock.newCondition();
    // 缓存区空的条件变量
    private final Condition empty = lock.newCondition();

    public Buffer(){
    }

    // 生产者生产商品
    public void produceAGood(){
        // 获取锁
        lock.lock();

        while (isFull){
            try {
                full.await();
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
        }

        // 开始生产
        GoodNum += 1;
        if(GoodNum == MAX){
            isFull = true;
        }

        // 如果生产之前，缓存区为空
        if(isEmpty){
            isEmpty = false;

            // 唤醒消费者进程
            empty.signalAll();
        }

        System.out.println(Thread.currentThread().getName()+" 生产了第 " + (GoodNum) + " 个商品....");

        // 释放锁
        lock.unlock();
    }

    // 消费者消费商品
    public void consumeAGood(){
        // 获得锁
        lock.lock();

        while (isEmpty){
            // 缓存区为空，等待唤醒
            try {
                empty.await();
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
        }

        // 开始消费
        GoodNum -= 1;
        if(GoodNum == 0){
            isEmpty = true;
        }

        // 如果消费之前缓存区已满
        if(isFull){
            isFull = false;
            // 唤醒生产者进程
            full.signalAll();
        }

        System.out.println(Thread.currentThread().getName()+" 消费了第 " + (GoodNum+1) + " 个商品....");

        // 释放锁
        lock.unlock();
    }

    public int getGoodNum() {
        return GoodNum;
    }
}
