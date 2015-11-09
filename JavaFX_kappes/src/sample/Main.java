package sample;

import com.sun.tools.doclets.internal.toolkit.util.DocFinder;
import javafx.application.Application;
import javafx.event.EventHandler;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.TextField;
import javafx.scene.input.KeyEvent;
import javafx.scene.layout.Pane;
import javafx.scene.layout.VBox;
import javafx.scene.text.Font;
import javafx.scene.text.FontPosture;
import javafx.scene.text.FontWeight;
import javafx.scene.text.Text;
import javafx.stage.Stage;



public class Main extends Application {

    @Override
    public void start(Stage primaryStage) throws Exception{

        Pane pane = new VBox();

        Parent root = FXMLLoader.load(getClass().getResource("sample.fxml"));
        primaryStage.setTitle("Hello World");
        primaryStage.setScene(new Scene(pane, 300, 275));
        primaryStage.show();

        runPython.main();

        Text text = new Text(runPython.getOut());
        text.setFont(Font.font("", FontWeight.NORMAL, FontPosture.REGULAR, 32));
        pane.getChildren().add(text);


    }


    public static void main(String[] args) {
        launch(args);

    }
}
