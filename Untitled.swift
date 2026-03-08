//
//  Untitled.swift
//  MatchMate
//
//  Created by Jason Chen on 2026-03-07.
//



import SwiftUI

struct LoginView: View {
    
    @State private var email = ""
    @State private var password = ""
    
    var body: some View {
        VStack(spacing: 20) {
            
            Text("MatchMate")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            TextField("Email", text: $email)
                .textFieldStyle(.roundedBorder)
                .padding(.horizontal)
            
            SecureField("Password", text: $password)
                .textFieldStyle(.roundedBorder)
                .padding(.horizontal)
            
            Button("Login") {
                // call backend API
            }
            .buttonStyle(.borderedProminent)
            
            Button("Create Account") {
                
            }
        }
    }
}



struct DataUploadView: View {
    
    var body: some View {
        
        VStack(spacing: 25) {
            
            Text("Build Your Personality Profile")
                .font(.title2)
            
            Button("Upload Data File") {
                
            }
            
            Button("Connect Google Data") {
                
            }
            
            Button("Generate Matches") {
                
            }
        }
    }
}

struct MatchResultsView: View {
    
    var body: some View {
        
        List {
            
            VStack(alignment: .leading) {
                Text("Alex")
                    .font(.headline)
                
                Text("Compatibility: 91%")
                    .font(.subheadline)
                
                Text("Shared interests: startups, fitness, AI")
            }
            
            VStack(alignment: .leading) {
                Text("Sarah")
                    .font(.headline)
                
                Text("Compatibility: 87%")
                    .font(.subheadline)
                
                Text("Shared interests: travel, design, running")
            }
        }
    }
}
