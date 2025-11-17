import React, { useState } from "react";

const LoginRegister = ({ onLoginSuccess }) => {
  const [isLoginView, setIsLoginView] = useState(true);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const toggleView = () => {
    setIsLoginView(!isLoginView);
    setName("");
    setEmail("");
    setPassword("");
    setError("");
    setIsLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    if (isLoginView) {
      try {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch('http://localhost:3000/token', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: formData.toString(),
        });

        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || "Error al iniciar sesión");
        }

        const data = await response.json();
        onLoginSuccess(data.access_token);

      } catch (err) {
        console.error("Error de login:", err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }

    } else {
      try {
        const response = await fetch('http://localhost:3000/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ name, email, password }),
        });

        if (!response.ok) {
          const errData = await response.json();
          if (Array.isArray(errData.detail)) {
            throw new Error(errData.detail[0].msg); 
          }
          throw new Error(errData.detail || "Error al registrarse");
        }
        
        alert("¡Registro exitoso! Ahora puedes iniciar sesión.");
        toggleView();

      } catch (err) {
        console.error("Error de registro:", err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <div className="w-full max-w-3xl bg-white shadow-lg rounded-xl border border-slate-200 overflow-hidden flex">
        <div className="flex-1 p-12 bg-slate-50 border-r border-slate-200 flex flex-col justify-center">
          <h1 className="text-4xl font-bold text-slate-800">Tutor de Matemáticas</h1>
          <p className="mt-3 text-slate-600 text-sm">
            Aprende, practica y resuelve con tu asistente matemático inteligente.
          </p>
        </div>

        <div className="flex-1 p-12">
          <h2 className="text-2xl font-semibold text-slate-800 mb-6">
            {isLoginView ? "Iniciar sesión" : "Registrarse"}
          </h2>

          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-300 text-red-700 rounded-lg text-sm text-center">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLoginView && (
              <input
                type="text"
                placeholder="Nombre"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                disabled={isLoading}
                className="w-full p-3 rounded-lg bg-slate-100 border border-slate-300 text-slate-800 focus:ring-2 focus:ring-sky-500 outline-none disabled:opacity-50"
              />
            )}

            <input
              type="email"
              placeholder="Correo electrónico"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
              className="w-full p-3 rounded-lg bg-slate-100 border border-slate-300 text-slate-800 focus:ring-2 focus:ring-sky-500 outline-none disabled:opacity-50"
            />

            <input
              type="password"
              placeholder="Contraseña"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
              className="w-full p-3 rounded-lg bg-slate-100 border border-slate-300 text-slate-800 focus:ring-2 focus:ring-sky-500 outline-none disabled:opacity-50"
            />

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-sky-600 text-white py-3 mt-4 rounded-lg font-semibold hover:bg-sky-700 transition-colors disabled:bg-slate-400 disabled:cursor-not-allowed"
            >
              {isLoading 
                ? 'Cargando...' 
                : (isLoginView ? "Entrar" : "Crear cuenta")
              }
            </button>
          </form>
          <div className="mt-6 text-center text-sm text-slate-600">
            {isLoginView ? (
              <p>
                ¿No tienes cuenta?{" "}
                <button
                  onClick={toggleView}
                  disabled={isLoading}
                  className="text-sky-600 hover:underline font-medium disabled:text-slate-400"
                >
                  Crear una aquí
                </button>
              </p>
            ) : (
              <p>
                ¿Ya tienes una cuenta?{" "}
                <button
                  onClick={toggleView}
                  disabled={isLoading}
                  className="text-sky-600 hover:underline font-medium disabled:text-slate-400"
                >
                  Inicia sesión
                </button>
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginRegister;
