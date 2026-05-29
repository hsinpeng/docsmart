def main():
    try:
        print("Hello from docsmart!")

    except Exception as e:
        print(f"Unknown Error: {e}") 

    finally: # This ALWAYS runs, ensuring every resource is closed even if an error occurs
        pass

if __name__ == "__main__":
    main()
