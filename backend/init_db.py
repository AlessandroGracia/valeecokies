"""
Script de inicialización de la base de datos - ACTUALIZADO.

Crea un usuario administrador inicial y algunos productos de ejemplo.
"""

import sys
sys.path.append('.')

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models import User, Product, Customer, UserRole
import bcrypt

def hash_password(password: str) -> str:
    """Encripta una contraseña usando bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def init_db():
    """Inicializa la base de datos con datos de ejemplo"""
    
    print("🗑️ Vaciando base de datos antigua...")
    Base.metadata.drop_all(bind=engine)
    
    print("🚀 Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Verificar si ya existe un usuario admin
        existing_admin = db.query(User).filter(User.username == "admin").first()
        
        if existing_admin:
            print("⚠️  Ya existe un usuario administrador.")
        else:
            print("👤 Creando usuario administrador...")
            admin_user = User(
                username="admin",
                email="admin@galletas.com",
                hashed_password=hash_password("admin123"),
                full_name="Administrador Principal",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            print("✅ Usuario admin creado (username: admin, password: admin123)")
        
        # Crear un vendedor de ejemplo
        existing_vendedor = db.query(User).filter(User.username == "vendedor1").first()
        
        if not existing_vendedor:
            print("👤 Creando usuario vendedor...")
            vendedor = User(
                username="vendedor1",
                email="vendedor@galletas.com",
                hashed_password=hash_password("vendedor123"),
                full_name="Juan Pérez",
                role=UserRole.VENDEDOR,
                is_active=True
            )
            db.add(vendedor)
            print("✅ Usuario vendedor creado (username: vendedor1, password: vendedor123)")
        
        # Productos de ejemplo (Menú real)
        productos_ejemplo = [
            # ==== GALLETAS ====
            {"code": "GAL-001", "name": "Explosión de Chocolate", "description": "Galleta explosión de chocolate", "category": "cookies", "cost_price": 1.00, "sale_price": 2.00, "stock_quantity": 40, "min_stock": 10, "unit": "unidad"},
            {"code": "GAL-002", "name": "Oreo", "description": "Galleta de Oreo", "category": "cookies", "cost_price": 1.00, "sale_price": 2.00, "stock_quantity": 40, "min_stock": 10, "unit": "unidad"},
            {"code": "GAL-003", "name": "Kinder", "description": "Galleta especial de Kinder", "category": "cookies", "cost_price": 1.25, "sale_price": 2.50, "stock_quantity": 30, "min_stock": 10, "unit": "unidad"},
            {"code": "GAL-004", "name": "Pistacho", "description": "Galleta premium de Pistacho", "category": "cookies", "cost_price": 1.60, "sale_price": 3.25, "stock_quantity": 25, "min_stock": 5, "unit": "unidad"},
            {"code": "GAL-005", "name": "Chocolate", "description": "Galleta clásica de chocolate", "category": "cookies", "cost_price": 1.00, "sale_price": 2.00, "stock_quantity": 50, "min_stock": 10, "unit": "unidad"},
            {"code": "GAL-006", "name": "M&M", "description": "Galleta con confites M&M", "category": "cookies", "cost_price": 1.00, "sale_price": 2.00, "stock_quantity": 40, "min_stock": 10, "unit": "unidad"},
            {"code": "GAL-007", "name": "Fiesta", "description": "Galleta Fiesta", "category": "cookies", "cost_price": 1.00, "sale_price": 2.00, "stock_quantity": 35, "min_stock": 10, "unit": "unidad"},
            {"code": "GAL-008", "name": "Kit-Kat", "description": "Galleta con trozos de Kit-Kat", "category": "cookies", "cost_price": 1.00, "sale_price": 2.00, "stock_quantity": 30, "min_stock": 10, "unit": "unidad"},
            {"code": "GAL-009", "name": "Chispas de Chocolate", "description": "Galleta tradicional con chispas de chocolate", "category": "cookies", "cost_price": 0.75, "sale_price": 1.50, "stock_quantity": 50, "min_stock": 10, "unit": "unidad"},
            
            # ==== BEBIDAS ====
            {"code": "BEB-001", "name": "Ice-Coffee", "description": "Café helado refrescante", "category": "bebidas", "cost_price": 1.00, "sale_price": 2.00, "stock_quantity": 50, "min_stock": 5, "unit": "vaso"},
            {"code": "BEB-002", "name": "Milkshake", "description": "Batido cremoso", "category": "bebidas", "cost_price": 1.75, "sale_price": 3.50, "stock_quantity": 30, "min_stock": 5, "unit": "vaso"},
            {"code": "BEB-003", "name": "Vaso de Leche", "description": "Vaso de leche fría o caliente", "category": "bebidas", "cost_price": 0.25, "sale_price": 0.50, "stock_quantity": 100, "min_stock": 20, "unit": "vaso"},
            
            # ==== POSTRES ====
            {"code": "POS-001", "name": "Rebanada", "description": "Rebanada tradicional", "category": "postres", "cost_price": 0.50, "sale_price": 1.00, "stock_quantity": 20, "min_stock": 5, "unit": "unidad"},
            {"code": "POS-002", "name": "Mojada de Chocolate", "description": "Torta mojada de chocolate", "category": "postres", "cost_price": 1.25, "sale_price": 2.50, "stock_quantity": 15, "min_stock": 3, "unit": "porción"},
            {"code": "POS-003", "name": "Cheesecake de Oreo", "description": "Cheesecake con base y trozos de Oreo", "category": "postres", "cost_price": 1.75, "sale_price": 3.50, "stock_quantity": 12, "min_stock": 2, "unit": "porción"},
            {"code": "POS-004", "name": "Cheesecake de Nutella", "description": "Cheesecake mezclado con Nutella", "category": "postres", "cost_price": 1.75, "sale_price": 3.50, "stock_quantity": 12, "min_stock": 2, "unit": "porción"},
            {"code": "POS-005", "name": "Cheesecake de Maracuyá", "description": "Cheesecake con jalea de maracuyá", "category": "postres", "cost_price": 1.75, "sale_price": 3.50, "stock_quantity": 10, "min_stock": 2, "unit": "porción"},
            {"code": "POS-006", "name": "Cheesecake de Pistacho", "description": "Cheesecake premium de pistacho", "category": "postres", "cost_price": 2.00, "sale_price": 4.00, "stock_quantity": 8, "min_stock": 2, "unit": "porción"},
        ]
        
        print("🍪 Creando productos de ejemplo...")
        for producto_data in productos_ejemplo:
            existing = db.query(Product).filter(Product.code == producto_data["code"]).first()
            if not existing:
                producto = Product(**producto_data)
                db.add(producto)
                print(f"   ✅ {producto_data['name']}")
        
        # Crear clientes de ejemplo
        clientes_ejemplo = [
            {
                "full_name": "María González",
                "email": "maria@ejemplo.com",
                "phone": "0999999999",
                "id_number": "0123456789",
                "address": "Av. Principal 123",
                "city": "Quito"
            },
            {
                "full_name": "Carlos Rodríguez",
                "email": "carlos@ejemplo.com",
                "phone": "0988888888",
                "id_number": "0987654321",
                "address": "Calle Secundaria 456",
                "city": "Guayaquil"
            },
            {
                "full_name": "Ana Martínez",
                "email": "ana@ejemplo.com",
                "phone": "0977777777",
                "id_number": "1122334455",
                "address": "Av. 10 de Agosto 789",
                "city": "Cuenca"
            }
        ]
        
        print("👥 Creando clientes de ejemplo...")
        for cliente_data in clientes_ejemplo:
            existing = db.query(Customer).filter(Customer.email == cliente_data["email"]).first()
            if not existing:
                cliente = Customer(**cliente_data)
                db.add(cliente)
                print(f"   ✅ {cliente_data['full_name']}")
        
        db.commit()
        print("\n🎉 ¡Base de datos inicializada con éxito!")
        print("\n📋 CREDENCIALES DE ACCESO:")
        print("=" * 50)
        print("Administrador:")
        print("  Usuario: admin")
        print("  Contraseña: admin123")
        print("\nVendedor:")
        print("  Usuario: vendedor1")
        print("  Contraseña: vendedor123")
        print("=" * 50)
        print("\n⚠️  IMPORTANTE: Cambia estas contraseñas en producción!")
        print("\n📊 DATOS CREADOS:")
        print(f"  • {len(productos_ejemplo)} productos")
        print(f"  • {len(clientes_ejemplo)} clientes")
        print("  • 1 producto con stock bajo (GAL005) para probar alertas")
        
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("   INICIALIZACIÓN DE BASE DE DATOS")
    print("   Sistema de Facturación - Galletas")
    print("=" * 50)
    print()
    init_db()
