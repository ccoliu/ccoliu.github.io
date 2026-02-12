# ---------------------------------------------------
# Codoctopus — Plagiarism Checker
# Copied from Servers/PlagiarismChecker.py (unchanged)
# ---------------------------------------------------

import ast
import Levenshtein


class ASTAnalyzer:
    def get_ast_structure(self, code):
        """Convert code to AST structure, extracting node names."""
        try:
            tree = ast.parse(code)
            return [node.__class__.__name__ for node in ast.walk(tree)]
        except Exception as e:
            print(f"AST Parsing Error: {e}")
            return []

    def compare_ast(self, code1, code2):
        """Compare AST structure similarity of two code snippets."""
        ast1 = set(self.get_ast_structure(code1))
        ast2 = set(self.get_ast_structure(code2))
        intersection = ast1.intersection(ast2)
        union = ast1.union(ast2)

        similarity = len(intersection) / len(union) if union else 0
        return similarity


class LevenshteinAnalyzer:
    def clean_code(self, code):
        """Clean code by removing whitespace."""
        return "".join(code.split())

    def compare_levenshtein(self, code1, code2):
        """Compare string similarity of two code snippets."""
        code1_clean = self.clean_code(code1)
        code2_clean = self.clean_code(code2)
        similarity = Levenshtein.ratio(code1_clean, code2_clean)
        similarity = f"Levenshtein Result: {similarity * 100:.2f}%" + "\n"
        return similarity


class PlagiarismChecker(ASTAnalyzer, LevenshteinAnalyzer):
    def combined_similarity(self, code1, code2, ast_weight=0.85, lev_weight=0.15):
        """Calculate weighted AST + Levenshtein similarity."""
        output_string = ""
        ast_sim = self.compare_ast(code1, code2)
        output_string += f"AST Result: {ast_sim * 100:.2f}%" + "\n"
        lev_sim = self.compare_levenshtein(code1, code2)
        output_string += f"Levenshtein Result: {lev_sim * 100:.2f}%" + "\n"
        weighted_similarity = ast_weight * ast_sim + lev_weight * lev_sim
        output_string += f"Combined Similarity: {weighted_similarity * 100:.2f}%"

        return output_string
