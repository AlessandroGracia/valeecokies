import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Lock, User, AlertCircle, Loader2, ArrowRight } from 'lucide-react';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [showConfig, setShowConfig] = useState(false);
  const [tempUrl, setTempUrl] = useState(localStorage.getItem('backend_url') || 'http://127.0.0.1:8000');
  const { login, loading } = useAuth();

  const handleSaveConfig = () => {
    localStorage.setItem('backend_url', tempUrl);
    setShowConfig(false);
    window.location.reload(); // Recargar para que el servicio de API tome la nueva URL
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!username || !password) {
      setError('Por favor completa todos los campos.');
      return;
    }

    try {
      await login(username, password);
    } catch (err) {
      setError(err.message || 'Usuario o contraseña incorrectos.');
    }
  };

  return (
    <div className="min-h-screen w-full flex relative overflow-hidden">

      {/* ===== PANEL IZQUIERDO: BRANDING ===== */}
      <div className="hidden lg:flex lg:w-[45%] bg-gradient-to-br from-amber-600 via-orange-500 to-amber-700 relative flex-col items-center justify-center p-12 text-white overflow-hidden">

        {/* Patrón de puntos decorativo */}
        <div className="absolute inset-0 opacity-[0.07]" style={{
          backgroundImage: 'radial-gradient(circle, white 1px, transparent 1px)',
          backgroundSize: '24px 24px'
        }} />

        {/* Círculos ambient */}
        <div className="absolute -top-20 -left-20 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-blob" />
        <div className="absolute -bottom-32 -right-20 w-[30rem] h-[30rem] bg-amber-800/20 rounded-full blur-3xl animate-blob animation-delay-2000" />

        {/* Contenido */}
        <div className="relative z-10 text-center animate-fadeIn">
          <div className="w-36 h-36 mx-auto mb-8 rounded-[2.5rem] overflow-hidden shadow-2xl shadow-black/30 border-4 border-white/30 hover:scale-105 transition-transform duration-500 animate-float">
            <img src="/logo.png" alt="Valeecokies" className="w-full h-full object-cover" />
          </div>

          <h1 className="text-5xl font-extrabold tracking-tight mb-3 font-['Poppins'] drop-shadow-lg">
            Valeecokies
          </h1>
          <p className="text-lg text-white/80 font-medium max-w-xs mx-auto leading-relaxed">
            Sistema de Punto de Venta
          </p>

          <div className="mt-10 flex items-center justify-center gap-6 text-white/60 text-sm">
            <span className="flex items-center gap-1.5">🍪 Galletas</span>
            <span className="w-1 h-1 rounded-full bg-white/40" />
            <span className="flex items-center gap-1.5">🍰 Postres</span>
            <span className="w-1 h-1 rounded-full bg-white/40" />
            <span className="flex items-center gap-1.5">🥤 Bebidas</span>
          </div>
        </div>
      </div>

      {/* ===== PANEL DERECHO: FORMULARIO ===== */}
      <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-stone-50 to-amber-50/40 p-6 sm:p-12 relative">

        {/* Subtle background pattern */}
        <div className="absolute inset-0 opacity-[0.03]" style={{
          backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23000000\' fill-opacity=\'1\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")'
        }} />

        <div className="relative z-10 w-full max-w-md animate-scaleIn">

          {/* Logo visible solo en mobile */}
          <div className="lg:hidden text-center mb-8">
            <div className="w-24 h-24 mx-auto mb-4 rounded-2xl overflow-hidden shadow-xl border-4 border-white/60">
              <img src="/logo.png" alt="Valeecokies" className="w-full h-full object-cover" />
            </div>
            <h1 className="text-3xl font-extrabold text-gray-900 font-['Poppins']">Valeecokies</h1>
          </div>

          {/* Encabezado */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 font-['Poppins']">Bienvenido de vuelta</h2>
            <p className="text-gray-500 mt-1">Ingresa tus credenciales para continuar</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">

            {error && (
              <div className="flex items-center gap-2 p-4 text-sm text-red-700 bg-red-50 rounded-xl border border-red-100 animate-fadeIn">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <p>{error}</p>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">Usuario</label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none text-gray-400 group-focus-within:text-amber-600 transition-colors">
                    <User className="w-5 h-5" />
                  </div>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="block w-full pl-11 pr-4 py-3.5 bg-white border border-gray-200 rounded-xl text-gray-900 text-sm focus:ring-2 focus:ring-amber-500/40 focus:border-amber-500 hover:border-gray-300 transition-all outline-none shadow-sm"
                    placeholder="ej: vendedor1"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1.5">Contraseña</label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none text-gray-400 group-focus-within:text-amber-600 transition-colors">
                    <Lock className="w-5 h-5" />
                  </div>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="block w-full pl-11 pr-4 py-3.5 bg-white border border-gray-200 rounded-xl text-gray-900 text-sm focus:ring-2 focus:ring-amber-500/40 focus:border-amber-500 hover:border-gray-300 transition-all outline-none shadow-sm"
                    placeholder="••••••••"
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="relative w-full flex items-center justify-center gap-2 px-4 py-3.5 text-sm font-semibold text-white transition-all bg-gradient-to-r from-amber-600 to-orange-600 rounded-xl hover:from-amber-500 hover:to-orange-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-amber-500 disabled:opacity-70 shadow-lg shadow-amber-600/25 hover:shadow-xl hover:shadow-amber-600/35 hover:-translate-y-0.5 active:translate-y-0 active:shadow-md"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  Ingresar al Sistema
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-10 text-center flex flex-col items-center gap-4">
            <button 
              onClick={() => setShowConfig(true)}
              className="text-xs text-amber-600 hover:text-amber-800 flex items-center gap-1 transition-colors"
            >
              <Lock className="w-3 h-3" />
              Configurar Servidor
            </button>
            <p className="text-xs text-gray-400">Valeecokies POS · © {new Date().getFullYear()}</p>
          </div>
        </div>
      </div>

      {/* Modal de Configuración de IP */}
      {showConfig && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-sm border border-gray-100">
            <h3 className="text-lg font-bold mb-4 text-gray-800">Escritorio de Red</h3>
            <p className="text-sm text-gray-600 mb-4">Ingresa la dirección IP o la URL de tu servidor en la nube.</p>
            
            <input
              type="text"
              value={tempUrl}
              onChange={(e) => setTempUrl(e.target.value)}
              placeholder="http://192.168.1.15:8000"
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl mb-6 text-sm outline-none focus:ring-2 focus:ring-amber-500"
            />
            
            <div className="flex gap-3">
              <button 
                onClick={() => setShowConfig(false)}
                className="flex-1 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
              >
                Cancelar
              </button>
              <button 
                onClick={handleSaveConfig}
                className="flex-1 px-4 py-2 text-sm font-bold text-white bg-amber-600 hover:bg-amber-700 rounded-xl shadow-lg transition-all"
              >
                Guardar y Reiniciar
              </button>
            </div>
          </div>
        </div>
      )}

      <style dangerouslySetInnerHTML={{__html: `
        @keyframes blob {
          0% { transform: translate(0px, 0px) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
          100% { transform: translate(0px, 0px) scale(1); }
        }
        .animate-blob { animation: blob 8s infinite; }
        .animation-delay-2000 { animation-delay: 2s; }
      `}} />
    </div>
  );
};

export default Login;
