//
//  DataUploadView.swift
//  MatchMate
//
//  Development only: placeholder for data upload (Chrome/YouTube etc.) before going to Home.
//

import SwiftUI

struct DataUploadView: View {
    @Binding var path: NavigationPath
    @EnvironmentObject var appState: AppState
    @State private var uploaded = false

    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "arrow.up.doc.fill")
                .font(.system(size: 50))
                .foregroundColor(.accentColor)

            Text("Data upload (development only)")
                .font(.headline)
                .multilineTextAlignment(.center)

            Text("In production this step would upload Chrome, YouTube, or other data for behavior-based matching.")
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)

            if !uploaded {
                Button(action: {
                    uploaded = true
                    appState.finishSignUp()
                }) {
                    Text("Skip / Done")
                        .fontWeight(.semibold)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.accentColor)
                        .foregroundColor(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .padding(.horizontal, 32)
                .padding(.top, 20)
            }
        }
        .padding(24)
        .navigationTitle("Data upload")
        .navigationBarTitleDisplayMode(.inline)
    }
}

#Preview {
    NavigationStack {
        DataUploadView(path: .constant(NavigationPath()))
            .environmentObject(AppState())
    }
}
