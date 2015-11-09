package sample;

import java.io.*;
import java.util.ArrayList;

/**
 * Created by yo on 09/11/15.
 */
public class runPython {

    static ArrayList out = new ArrayList<String>();

    public static void main(){

        OutputStream stdin = null;
        InputStream stderr = null;
        InputStream stdout = null;
        String line;
        //change argument
        String arg1 = "-h";

        try{

            String pythonPath = "../framework/cli.py";
            ProcessBuilder pb = new ProcessBuilder("python", pythonPath, ""+arg1);
            Process p = pb.start();

            stdin = p.getOutputStream();
            stdout = p.getInputStream();
            stderr = p.getErrorStream();

            /*line = " 1" + "\n";
            stdin.write(line.getBytes());
            stdin.flush();

            stdin.close();
            */


             BufferedReader brCleanUp = new BufferedReader(new InputStreamReader(stdout));
                while ((line = brCleanUp.readLine()) != null){
                    System.out.println("stdout" + line);
                    out.add(line);
                }
                brCleanUp.close();


             brCleanUp = new BufferedReader(new InputStreamReader(stderr));
                while ((line = brCleanUp.readLine()) != null){
                    System.out.println("stderr" + line);
                    out.add(line);
                }
                brCleanUp.close();

        }
        catch(Exception e){System.out.println(e);}
    }

    public static String getOut(){
         for(int i = 0; i< out.size(); i++){
             String output = out.toString()+"\n";
             return output;
         }
        return null;
    }

}
