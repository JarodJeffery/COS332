import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.util.Base64;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.SSLSocketFactory;

public class A6 {
    public static void main(String[] args) throws Exception {

        String username = "u18003193@tuks.co.za";
        final String password = "wbdh yqyu ekwe ndjk";// lbhs tybh ztue
        String recipient = "jarodjeffery@gmail.com";// aqye kshd cmqe idui
        String subject = "Test Email";
        String body = "Testing";

        String host = "smtp.gmail.com";
        int port = 465;

        SSLSocketFactory factory = (SSLSocketFactory) SSLSocketFactory.getDefault();
        SSLSocket socket = (SSLSocket) factory.createSocket(host, port);
        BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));

        String line = reader.readLine();
        System.out.println(line);

        writer.write("EHLO " + host + "\r\n");
        writer.flush();
        line = reader.readLine();
        System.out.println(line);

        writer.write("AUTH LOGIN\r\n");
        writer.flush();
        line = reader.readLine();
        System.out.println(line);

        String encodedUsername = Base64.getEncoder().encodeToString(username.getBytes());
        writer.write(encodedUsername + "\r\n");
        writer.flush();
        line = reader.readLine();
        System.out.println(line);

        String encodedPassword = Base64.getEncoder().encodeToString(password.getBytes());
        writer.write(encodedPassword + "\r\n");
        writer.flush();
        line = reader.readLine();
        System.out.println(line);

        writer.write("MAIL FROM:<" + username + ">\r\n");
        writer.flush();
        line = reader.readLine();
        System.out.println(line);

        writer.write("RCPT TO:<" + recipient + ">\r\n");
        writer.flush();
        line = reader.readLine();
        System.out.println(line);

        writer.write("DATA\r\n");
        writer.flush();
        line = reader.readLine();
        System.out.println(line);

        writer.write("Subject: " + subject + "\r\n\r\n" + body + "\r\n.\r\n");
        writer.flush();
        line = reader.readLine();
        System.out.println(line);

        writer.write("QUIT\r\n");
        writer.flush();
        line = reader.readLine();
        System.out.println(line);
        // System.out.println("test");

        writer.close();
        reader.close();
        socket.close();

        System.out.println("email sent successfully");
    }
}