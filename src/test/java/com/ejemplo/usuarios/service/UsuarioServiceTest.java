package com.ejemplo.usuarios.service;

import com.ejemplo.usuarios.model.Usuario;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

class UsuarioServiceTest {

    private UsuarioService service;

    @BeforeEach
    void setUp() {
        service = new UsuarioService();
    }

    @Test
    void obtenerTodos_retornaListaNoVacia() {
        List<Usuario> usuarios = service.obtenerTodos();
        assertFalse(usuarios.isEmpty());
    }

    @Test
    void guardar_agregaUsuarioCorrecto() {
        Usuario nuevo = new Usuario(null, "Carlos", "carlos@test.com");
        Usuario guardado = service.guardar(nuevo);
        assertNotNull(guardado.getId());
        assertEquals("Carlos", guardado.getNombre());
    }

    @Test
    void obtenerPorId_retornaUsuarioExistente() {
        Usuario guardado = service.guardar(new Usuario(null, "María", "maria@test.com"));
        Optional<Usuario> resultado = service.obtenerPorId(guardado.getId());
        assertTrue(resultado.isPresent());
        assertEquals("María", resultado.get().getNombre());
    }

    @Test
    void obtenerPorId_retornaVacioSiNoExiste() {
        Optional<Usuario> resultado = service.obtenerPorId(999L);
        assertTrue(resultado.isEmpty());
    }

    @Test
    void actualizar_modificaUsuarioExistente() {
        Usuario guardado = service.guardar(new Usuario(null, "Pedro", "pedro@test.com"));
        Usuario actualizado = new Usuario(null, "Pedro Actualizado", "pedro2@test.com");
        Optional<Usuario> resultado = service.actualizar(guardado.getId(), actualizado);
        assertTrue(resultado.isPresent());
        assertEquals("Pedro Actualizado", resultado.get().getNombre());
    }

    @Test
    void actualizar_retornaVacioSiNoExiste() {
        Optional<Usuario> resultado = service.actualizar(999L, new Usuario(null, "X", "x@x.com"));
        assertTrue(resultado.isEmpty());
    }

    @Test
    void eliminar_retornaTrueSiExiste() {
        Usuario guardado = service.guardar(new Usuario(null, "Elena", "elena@test.com"));
        assertTrue(service.eliminar(guardado.getId()));
    }

    @Test
    void eliminar_retornaFalseSiNoExiste() {
        assertFalse(service.eliminar(999L));
    }
}
