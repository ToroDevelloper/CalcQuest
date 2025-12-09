import sympy
from sympy import (
    symbols, Function, Derivative, exp, dsolve, Eq, 
    integrate, simplify, latex, parse_expr, sin, cos, tan, log, sqrt,
    Add, Mul, Pow, Symbol, sympify
)
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, 
    implicit_multiplication_application, convert_xor
)
import re


class Step:
    """
    Representa un paso en la solución de una ecuación diferencial.
    
    Attributes:
        latex: Expresión matemática en formato LaTeX
        explanation: Explicación en lenguaje natural del paso
        hint: Pista opcional para el estudiante
        step_type: Tipo de paso (identification, calculation, solution, etc.)
    """
    def __init__(self, latex: str, explanation: str, hint: str = "", step_type: str = "general"):
        self.latex = latex
        self.explanation = explanation
        self.hint = hint
        self.step_type = step_type
    
    def __repr__(self):
        return f"Step(type={self.step_type}, latex='{self.latex[:30]}...')"


class StepEngine:
    """
    Motor de resolución paso a paso para Ecuaciones Diferenciales.
    
    Este motor analiza ecuaciones diferenciales, identifica su tipo,
    y genera una secuencia de pasos explicativos para su resolución.
    
    Tipos soportados:
    - Ecuaciones Lineales de Primer Orden: y' + P(x)y = Q(x)
    - Ecuaciones de Variables Separables: dy/dx = f(x)g(y)
    - Ecuaciones Homogéneas
    """
    
    def __init__(self):
        self.x = symbols('x')
        self.y_func = Function('y')
        self.y = self.y_func(self.x)
        self.dy = Derivative(self.y, self.x)
        
        # Transformaciones para el parser
        self.transformations = (
            standard_transformations + 
            (implicit_multiplication_application, convert_xor)
        )
    
    def _preprocess_input(self, equation_str: str) -> str:
        """
        Preprocesa la entrada del usuario para convertirla a formato SymPy.
        
        Convierte notaciones comunes como:
        - y' -> Derivative(y(x), x)
        - y'' -> Derivative(y(x), x, x)
        - dy/dx -> Derivative(y(x), x)
        - e^x -> exp(x)
        """
        processed = equation_str.strip()
        
        # Reemplazar notaciones de derivadas
        # y''' -> Derivative(y(x), x, x, x)
        processed = re.sub(r"y'''", "Derivative(y(x), x, x, x)", processed)
        # y'' -> Derivative(y(x), x, x)
        processed = re.sub(r"y''", "Derivative(y(x), x, x)", processed)
        # y' -> Derivative(y(x), x)
        processed = re.sub(r"y'", "Derivative(y(x), x)", processed)
        
        # dy/dx -> Derivative(y(x), x)
        processed = re.sub(r"dy/dx", "Derivative(y(x), x)", processed)
        processed = re.sub(r"d²y/dx²", "Derivative(y(x), x, x)", processed)
        
        # e^(...) -> exp(...)
        processed = re.sub(r"e\^([a-zA-Z0-9]+)", r"exp(\1)", processed)
        processed = re.sub(r"e\^\(([^)]+)\)", r"exp(\1)", processed)
        
        # Reemplazar 'y' sola (sin derivada) por y(x)
        # Cuidado: no reemplazar la 'y' dentro de Derivative o y(x)
        processed = re.sub(r"(?<![a-zA-Z_])y(?!\(|'|[a-zA-Z])", "y(x)", processed)
        
        return processed
    
    def _parse_equation(self, equation_str: str):
        """
        Parsea la ecuación del usuario a una expresión SymPy.
        
        Args:
            equation_str: Ecuación en formato string
            
        Returns:
            Tuple (lhs, rhs) si hay '=', o (expr, 0) si no hay
        """
        processed = self._preprocess_input(equation_str)
        
        # Definir símbolos locales para el parser
        local_dict = {
            'x': self.x,
            'y': self.y,
            'exp': exp,
            'sin': sin,
            'cos': cos,
            'tan': tan,
            'log': log,
            'sqrt': sqrt,
            'Derivative': Derivative,
            'Function': Function
        }
        
        try:
            if '=' in processed:
                lhs_str, rhs_str = processed.split('=', 1)
                lhs = parse_expr(lhs_str.strip(), local_dict=local_dict, 
                               transformations=self.transformations)
                rhs = parse_expr(rhs_str.strip(), local_dict=local_dict,
                               transformations=self.transformations)
                return lhs, rhs
            else:
                expr = parse_expr(processed, local_dict=local_dict,
                                transformations=self.transformations)
                return expr, sympify(0)
        except Exception as e:
            raise ValueError(f"No se pudo parsear la ecuación: {e}")
    
    def identify_type(self, equation_str: str) -> str:
        """
        Identifica el tipo de ecuación diferencial.
        
        Args:
            equation_str: Ecuación en formato string
            
        Returns:
            Tipo de ecuación identificado
        """
        try:
            lhs, rhs = self._parse_equation(equation_str)
            eq = Eq(lhs, rhs)
            
            # Mover todo a un lado: lhs - rhs = 0
            expr = lhs - rhs
            
            # Buscar derivadas
            derivatives = expr.atoms(Derivative)
            
            if not derivatives:
                return "No es una Ecuación Diferencial"
            
            # Determinar el orden
            max_order = 0
            for deriv in derivatives:
                order = len(deriv.args) - 1  # Número de variables de diferenciación
                if order > max_order:
                    max_order = order
            
            # Intentar clasificar
            if max_order == 1:
                # Verificar si es lineal de primer orden
                # Forma: y' + P(x)*y = Q(x)
                if self._is_first_order_linear(expr):
                    return "Lineal de Primer Orden"
                elif self._is_separable(lhs, rhs):
                    return "Variables Separables"
                else:
                    return "Primer Orden (tipo por determinar)"
            elif max_order == 2:
                return "Segundo Orden"
            else:
                return f"Orden {max_order}"
                
        except Exception as e:
            return f"No identificado: {str(e)}"
    
    def _is_first_order_linear(self, expr) -> bool:
        """Verifica si la expresión es una EDO lineal de primer orden."""
        try:
            # Una EDO lineal de primer orden tiene la forma:
            # y' + P(x)*y + Q(x) = 0 (después de mover todo a un lado)
            
            # Verificar que y' aparece con coeficiente 1 o función de x
            # y que y aparece multiplicado solo por funciones de x
            
            # Simplificación: si tiene Derivative y y(x), y los exponentes son 1
            has_derivative = any(isinstance(term, Derivative) for term in expr.atoms(Derivative))
            
            # Verificar que y no aparece con potencias > 1
            y_terms = [term for term in expr.atoms(Pow) if self.y in term.free_symbols]
            for term in y_terms:
                if term.exp != 1:
                    return False
            
            return has_derivative
        except:
            return False
    
    def _is_separable(self, lhs, rhs) -> bool:
        """Verifica si la ecuación es de variables separables."""
        # dy/dx = f(x) * g(y)
        try:
            if isinstance(lhs, Derivative):
                # rhs debe ser producto de funciones de x y y separables
                # Simplificación por ahora
                return True
            return False
        except:
            return False
    
    def _extract_linear_coefficients(self, expr):
        """
        Extrae P(x) y Q(x) de una ecuación lineal de primer orden.
        Forma estándar: y' + P(x)*y = Q(x)
        """
        try:
            # Recolectar términos
            expr_expanded = sympy.expand(expr)
            
            # El coeficiente de y'
            dy_coeff = expr_expanded.coeff(self.dy)
            if dy_coeff == 0:
                dy_coeff = 1
            
            # Normalizar dividiendo por el coeficiente de y'
            if dy_coeff != 1:
                expr_expanded = expr_expanded / dy_coeff
            
            # El coeficiente de y(x)
            p_x = expr_expanded.coeff(self.y)
            
            # El término independiente (Q(x) pero con signo cambiado porque está del lado izquierdo)
            # expr = y' + P(x)*y - Q(x) = 0
            # Entonces Q(x) = -(términos sin y ni y')
            remaining = expr_expanded - self.dy - p_x * self.y
            q_x = -remaining
            
            return p_x, q_x
        except Exception as e:
            return None, None
    
    def solve_steps(self, equation_str: str) -> list:
        """
        Genera los pasos de solución para una ecuación diferencial.
        
        Args:
            equation_str: Ecuación en formato string del usuario
            
        Returns:
            Lista de objetos Step con la solución paso a paso
        """
        steps = []
        
        try:
            # Paso 0: Mostrar la ecuación original
            steps.append(Step(
                latex=equation_str,
                explanation="📝 Ecuación original ingresada por el usuario.",
                step_type="input"
            ))
            
            # Parsear la ecuación
            lhs, rhs = self._parse_equation(equation_str)
            eq = Eq(lhs, rhs)
            expr = lhs - rhs
            
            # Identificar el tipo
            eq_type = self.identify_type(equation_str)
            
            steps.append(Step(
                latex=latex(eq),
                explanation=f"🔍 Identificamos el tipo de ecuación: **{eq_type}**",
                hint="Observa la estructura de la ecuación para identificar su tipo.",
                step_type="identification"
            ))
            
            # Generar pasos según el tipo
            if eq_type == "Lineal de Primer Orden":
                steps.extend(self._solve_linear_first_order(expr, eq))
            elif eq_type == "Variables Separables":
                steps.extend(self._solve_separable(lhs, rhs, eq))
            else:
                steps.append(Step(
                    latex="",
                    explanation=f"⚠️ Aún no tenemos implementada la solución paso a paso para ecuaciones de tipo '{eq_type}'. ¡Próximamente!",
                    step_type="warning"
                ))
                
                # Intentar resolver con dsolve de todas formas
                try:
                    solution = dsolve(eq, self.y)
                    steps.append(Step(
                        latex=latex(solution),
                        explanation="✨ Solución general obtenida (sin pasos detallados):",
                        step_type="solution"
                    ))
                except:
                    pass
            
        except Exception as e:
            steps.append(Step(
                latex="",
                explanation=f"❌ Error al procesar la ecuación: {str(e)}",
                hint="Verifica la sintaxis de tu ecuación. Ejemplos válidos: y' + 2y = e^x, dy/dx = xy",
                step_type="error"
            ))
        
        return steps
    
    def _solve_linear_first_order(self, expr, eq) -> list:
        """
        Resuelve una EDO lineal de primer orden paso a paso.
        Forma: y' + P(x)y = Q(x)
        Método: Factor Integrante
        """
        steps = []
        
        # Paso 1: Forma estándar
        steps.append(Step(
            latex=r"y' + P(x) \cdot y = Q(x)",
            explanation="📐 La forma estándar de una EDO lineal de primer orden es: y' + P(x)·y = Q(x)",
            hint="Necesitamos identificar P(x) y Q(x) de nuestra ecuación.",
            step_type="theory"
        ))
        
        # Extraer coeficientes
        p_x, q_x = self._extract_linear_coefficients(expr)
        
        if p_x is not None:
            steps.append(Step(
                latex=f"P(x) = {latex(p_x)}, \\quad Q(x) = {latex(q_x)}",
                explanation=f"🔎 Identificamos los coeficientes:\n• P(x) = {latex(p_x)} (coeficiente de y)\n• Q(x) = {latex(q_x)} (término independiente)",
                step_type="calculation"
            ))
            
            # Paso 2: Factor Integrante
            steps.append(Step(
                latex=r"\mu(x) = e^{\int P(x) \, dx}",
                explanation="🔧 El **Factor Integrante** es la clave para resolver esta ecuación. Se calcula como μ(x) = e^(∫P(x)dx)",
                hint="El factor integrante 'mágicamente' convierte el lado izquierdo en una derivada de un producto.",
                step_type="theory"
            ))
            
            # Calcular la integral de P(x)
            try:
                integral_p = integrate(p_x, self.x)
                mu = exp(integral_p)
                
                steps.append(Step(
                    latex=f"\\int P(x) \\, dx = \\int {latex(p_x)} \\, dx = {latex(integral_p)}",
                    explanation=f"📊 Integramos P(x) = {latex(p_x)}",
                    step_type="calculation"
                ))
                
                steps.append(Step(
                    latex=f"\\mu(x) = e^{{{latex(integral_p)}}} = {latex(mu)}",
                    explanation=f"✨ El factor integrante es: μ(x) = {latex(mu)}",
                    step_type="calculation"
                ))
                
                # Paso 3: Multiplicar por el factor integrante
                steps.append(Step(
                    latex=f"{latex(mu)} \\cdot y' + {latex(mu)} \\cdot {latex(p_x)} \\cdot y = {latex(mu)} \\cdot {latex(q_x)}",
                    explanation="🔄 Multiplicamos ambos lados de la ecuación por el factor integrante μ(x)",
                    step_type="calculation"
                ))
                
                # Paso 4: Reconocer la derivada del producto
                steps.append(Step(
                    latex=f"\\frac{{d}}{{dx}}\\left[ {latex(mu)} \\cdot y \\right] = {latex(simplify(mu * q_x))}",
                    explanation="🎯 ¡El lado izquierdo ahora es la derivada de un producto! d/dx[μ(x)·y]",
                    hint="Esta es la 'magia' del factor integrante.",
                    step_type="insight"
                ))
                
                # Paso 5: Integrar ambos lados
                rhs_integral = integrate(mu * q_x, self.x)
                
                steps.append(Step(
                    latex=f"{latex(mu)} \\cdot y = \\int {latex(simplify(mu * q_x))} \\, dx",
                    explanation="📐 Integramos ambos lados respecto a x",
                    step_type="calculation"
                ))
                
                steps.append(Step(
                    latex=f"{latex(mu)} \\cdot y = {latex(rhs_integral)} + C",
                    explanation="📊 Resultado de la integral (no olvidar la constante C)",
                    step_type="calculation"
                ))
                
                # Paso 6: Despejar y
                y_solution = simplify(rhs_integral / mu)
                C = symbols('C')
                y_general = y_solution + C / mu
                
                steps.append(Step(
                    latex=f"y = \\frac{{{latex(rhs_integral)} + C}}{{{latex(mu)}}}",
                    explanation="🎉 Despejamos y dividiendo entre μ(x)",
                    step_type="calculation"
                ))
                
                # Simplificar si es posible
                y_simplified = simplify(y_general)
                
                steps.append(Step(
                    latex=f"y = {latex(y_simplified)}",
                    explanation="✅ **Solución General** de la ecuación diferencial",
                    hint="C es la constante de integración. Su valor se determina con condiciones iniciales.",
                    step_type="solution"
                ))
                
            except Exception as e:
                steps.append(Step(
                    latex="",
                    explanation=f"⚠️ No se pudo completar el cálculo: {str(e)}",
                    step_type="error"
                ))
        else:
            steps.append(Step(
                latex="",
                explanation="⚠️ No se pudieron extraer los coeficientes P(x) y Q(x) de la ecuación.",
                hint="Intenta escribir la ecuación en forma estándar: y' + P(x)y = Q(x)",
                step_type="error"
            ))
        
        return steps
    
    def _solve_separable(self, lhs, rhs, eq) -> list:
        """
        Resuelve una EDO de variables separables paso a paso.
        Forma: dy/dx = f(x)·g(y)
        """
        steps = []
        
        steps.append(Step(
            latex=r"\frac{dy}{dx} = f(x) \cdot g(y)",
            explanation="📐 Una ecuación de **variables separables** tiene la forma: dy/dx = f(x)·g(y)",
            hint="Podemos 'separar' las variables x e y a cada lado de la ecuación.",
            step_type="theory"
        ))
        
        steps.append(Step(
            latex=r"\frac{dy}{g(y)} = f(x) \, dx",
            explanation="🔄 Separamos las variables: todo lo que tiene 'y' a un lado, todo lo que tiene 'x' al otro.",
            step_type="calculation"
        ))
        
        steps.append(Step(
            latex=r"\int \frac{dy}{g(y)} = \int f(x) \, dx",
            explanation="📊 Integramos ambos lados",
            step_type="calculation"
        ))
        
        # Intentar resolver con dsolve
        try:
            solution = dsolve(eq, self.y)
            steps.append(Step(
                latex=latex(solution),
                explanation="✅ **Solución General** obtenida:",
                step_type="solution"
            ))
        except Exception as e:
            steps.append(Step(
                latex="",
                explanation=f"⚠️ La integración completa requiere más trabajo: {str(e)}",
                step_type="warning"
            ))
        
        return steps