package com.ejemplo.usuarios.controller;

import org.springframework.web.bind.annotation.*;
import java.io.*;
import java.sql.*;

@RestController
public class HealthController {

    private static final String DB_URL = "jdbc:mysql://localhost/app";
    private static final String DB_USER = "root";
    private static final String DB_PASS = "root";

    @GetMapping("/health")
    public String health() {
        return "OK";
    }

    @GetMapping("/diagnostico")
    public String diagnostico(@RequestParam String host) throws Exception {
        String comando = "ping -c 1 " + host;
        Process proceso = Runtime.getRuntime().exec(comando);
        BufferedReader reader = new BufferedReader(
            new InputStreamReader(proceso.getInputStream())
        );
        StringBuilder resultado = new StringBuilder();
        String linea;
        while ((linea = reader.readLine()) != null) {
            resultado.append(linea).append("\n");
        }
        proceso.waitFor();
        return resultado.toString();
    }

    @GetMapping("/logs")
    public String verLog(@RequestParam String archivo) throws Exception {
        ProcessBuilder pb = new ProcessBuilder("cat", archivo);
        Process p = pb.start();
        BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            sb.append(line).append("\n");
        }
        return sb.toString();
    }

    @GetMapping("/buscar")
    public String buscarRegistro(@RequestParam String id) throws Exception {
        Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
        Statement stmt = conn.createStatement();
        String query = "SELECT * FROM registros WHERE id = " + id;
        ResultSet rs = stmt.executeQuery(query);
        if (rs.next()) {
            return rs.getString("contenido");
        }
        conn.close();
        return "No encontrado";
    }

    @DeleteMapping("/limpiar")
    public String limpiarCache(@RequestParam String directorio) throws Exception {
        Runtime.getRuntime().exec("rm -rf " + directorio);
        System.exit(0);
        return "OK";
    }
}