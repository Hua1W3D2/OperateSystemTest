package com.test;

import javax.swing.*;
import javax.swing.border.*;
import javax.swing.plaf.metal.MetalBorders;
import java.awt.*;

public class Demo4 {

    public static void main(String[] args) {
        GuiWindow guiWindow = new GuiWindow();
        guiWindow.init();
    }

}

class GuiWindow{
    private int width = 600;
    private int height = 500;

    private Toolkit tool = Toolkit.getDefaultToolkit();
    private Dimension dimension = tool.getScreenSize();
    private int scnWidth = dimension.width;
    private int scnHeight = dimension.height;

    JFrame frame = new JFrame("边框展示");
    JPanel panel = new JPanel();

    public void init(){
        frame.setBounds((scnWidth-width)/2,(scnHeight-height)/2,width,height);
        frame.setLayout(new GridLayout(2,4));
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);


//        Border bevelBorder = BorderFactory.createBevelBorder(BevelBorder.RAISED, Color.red, Color.blue, Color.green, Color.gray);
//        frame.add(addBorder(bevelBorder,"BevelBorder"));
//
//        Border lineBorder = BorderFactory.createLineBorder(Color.yellow, 10);
//        frame.add(addBorder(lineBorder,"LineBorder"));
//
        Border emptyBorder = BorderFactory.createEmptyBorder(10, 20, 10, 15);
        frame.add(addBorder(emptyBorder,"EmptyBorder"));

        Border etchedBorder = BorderFactory.createEtchedBorder(EtchedBorder.LOWERED, Color.blue, Color.blue);
        frame.add(addBorder(etchedBorder,"EtchedBorder"));

        MatteBorder matteBorder = new MatteBorder(10,20,30,40,Color.yellow);
        frame.add(addBorder(matteBorder,"MatteBorder"));

//        TitledBorder titledBorder = new TitledBorder(new LineBorder(Color.yellow,10),"测试标题");
//        frame.add(addBorder(titledBorder,"TitleBorder"));
//
//        MatteBorder matteBorder = new MatteBorder(10,20,30,40,Color.yellow);
//        frame.add(addBorder(matteBorder,"MatteBorder"));
//
//        CompoundBorder compoundBorder = new CompoundBorder(new LineBorder(Color.red,30),
//                new TitledBorder(new LineBorder(Color.BLUE,10),"测试标题"));
//        frame.add(addBorder(compoundBorder,"CompoundBorder"));

        frame.setVisible(true);
    }

    public JPanel addBorder(Border border, String doc){
        JPanel jp = new JPanel();
        jp.add(new JLabel(doc));
        jp.setBorder(border);

        return jp;
    }

}
