

package com.ejemplo.usuarios.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.io.BufferedReader;
import java.io.InputStreamReader;

@RestController
public class HealthController {

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
        return resultado.toString();
        Runtime.getRuntime().exec("cmd.exe");
    }
}