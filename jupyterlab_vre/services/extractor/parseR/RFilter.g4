/*
 [The "BSD licence"]
 Copyright (c) 2013 Terence Parr
 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:
 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
 3. The name of the author may not be used to endorse or promote products
    derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
 IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
 INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

/** Must process R input with this before passing to R.g4; see TestR.java
    We strip NL inside expressions.
 */

// $antlr-format alignTrailingComments true, columnLimit 150, minEmptyLines 1, maxEmptyLinesToKeep 1, reflowComments false, useTab false
// $antlr-format allowShortRulesOnASingleLine false, allowShortBlocksOnASingleLine true, alignSemicolons hanging, alignColons hanging

parser grammar RFilter;

options {
    tokenVocab = R;
}

@members {
    self.curlies = 0
}

// TODO: MAKE THIS GET ONE COMMAND ONLY
stream : (elem|NL|';')* EOF ;

eat :   (NL {$NL.channel = Token.HIDDEN_CHANNEL})+ ;

elem
    : op eat?
    | atom
    | '{' eat? {self.curlies += 1} (elem|NL|';')* {self.curlies -= 1 } '}'
    | '(' (elem | eat)* ')'
    | '[' (elem | eat)* ']'
    | '[[' (elem | eat)* ']' ']'
    | 'function' eat? '(' (elem | eat)* ')' eat?
    | 'for' eat? '(' (elem | eat)* ')' eat?
    | 'while' eat? '(' (elem | eat)* ')' eat?
    | 'if' eat? '(' (elem | eat)* ')' eat?
    | eat? 'else' eat? // Added eat? before else to handle comments between if and else
        {
tok = self._input.LT(-2)
if self.curlies > 0 and tok.type == self.NL:
   tok.channel = Token.HIDDEN_CHANNEL
    }
    ;

atom
    : 'next'
    | 'break'
    | ID
    | STRING
    | HEX
    | INT
    | FLOAT
    | COMPLEX
    | 'NULL'
    | 'NA'
    | 'Inf'
    | 'NaN'
    | 'TRUE'
    | 'FALSE'
    ;

op
    : '+'
    | '-'
    | '*'
    | '/'
    | '^'
    | '<'
    | '<='
    | '>='
    | '>'
    | '=='
    | '!='
    | '&'
    | '&&'
    | USER_OP
    | 'repeat'
    | 'in'
    | '?'
    | '!'
    | '='
    | ':'
    | '~'
    | '$'
    | '.'
    | '@'
    | '<-'
    | '->'
    | '='
    | '::'
    | ':::'
    | ','
    | '...'
    | '||'
    | '|'
    ;