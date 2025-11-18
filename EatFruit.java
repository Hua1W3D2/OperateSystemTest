import java.util.concurrent.locks.*;

class Resource // 封装水果资源，提供放水果和吃水果方法。
{
    private String name;
    private static int ap = 0; // 苹果信号，0表示无，1表示有
    private static int or = 0; // 橘子信号，0表示无，1表示有
    private static int pz = 0; // 盘子有无水果信号，0表示无，1表示有

    Lock lock = new ReentrantLock(); // 锁对象

    Condition fmther_lock = lock.newCondition();// 爸妈共用监视器，可以唤醒爸妈其中一个放水果
    Condition son_lock = lock.newCondition(); // 儿子监视器
    Condition daughter_lock = lock.newCondition(); // 女儿监视器

    // 放水果,i=1表示是爸爸，i=2表示是妈妈
    void put(String name, int i) {
        lock.lock();
        try {
            Thread.sleep(500);
        } catch (Exception e) {
            e.printStackTrace();
        }
        try {
            while (pz == 1) // 盘子有水果
            {
                try {
                    fmther_lock.await();
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
            if (i == 1) // 爸爸
            {
                ap = 1;
                pz = 1;
                this.name = name; // 此处赋值防止线程中断名字不符（错乱）
                System.out.println(this.name + "放苹果");
                son_lock.signal();
            } else if (i == 2) // 妈妈
            {
                or = 1;
                pz = 1;
                this.name = name; // 此处赋值防止线程中断名字不符（错乱）
                System.out.println(this.name + "放橘子");
                daughter_lock.signal();
            }
        } finally {
            lock.unlock();
        }
    }

    // 吃水果,i=1表示是儿子，i=2表示是女儿
    void eat(String name, int i) {
        lock.lock();
        try {
            Thread.sleep(500);
        } catch (Exception e) {
            e.printStackTrace();
        }
        try {

            while (i == 1) // 儿子
            {
                while (ap == 0) {
                    try {
                        son_lock.await();
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
                ap = 0;
                pz = 0;
                this.name = name; // 此处赋值防止线程中断名字不符（错乱）
                System.out.println(this.name + "吃苹果");
                fmther_lock.signal();

            }
            while (i == 2) // 女儿
            {
                while (or == 0) {
                    try {
                        daughter_lock.await();
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
                or = 0;
                pz = 0;
                this.name = name; // 此处赋值防止线程中断名字不符（错乱）
                System.out.println(this.name + "吃橘子");
                fmther_lock.signal();
            }
        } finally {
            lock.unlock();
        }
    }
}

class FatherPut implements Runnable {
    private Resource r;

    FatherPut(Resource r) {
        this.r = r;
    }

    public void run() {
        while (true) {
            r.put("爸爸", 1);
        }
    }
}

class MotherPut implements Runnable {
    private Resource r;

    MotherPut(Resource r) {
        this.r = r;
    }

    public void run() {
        while (true) {
            r.put("妈妈", 2);
        }
    }
}

class SonEat implements Runnable {
    private Resource r;

    SonEat(Resource r) {
        this.r = r;
    }

    public void run() {
        while (true) {
            r.eat("儿子", 1);
        }
    }
}

class DaughterEat implements Runnable {
    private Resource r;

    DaughterEat(Resource r) {
        this.r = r;
    }

    public void run() {
        while (true) {
            r.eat("女儿", 2);
        }
    }
}

public class EatFruit {
    public static void main(String[] args) {
        Resource r = new Resource();

        FatherPut fa = new FatherPut(r);
        MotherPut mo = new MotherPut(r);
        SonEat son = new SonEat(r);
        DaughterEat dau = new DaughterEat(r);

        Thread t0 = new Thread(fa);
        Thread t1 = new Thread(mo);
        Thread t2 = new Thread(son);
        Thread t3 = new Thread(dau);
        t0.start();
        t1.start();
        t2.start();
        t3.start();
    }
}